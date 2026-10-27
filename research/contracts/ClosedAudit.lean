import Mathlib
import Aesop
import Lean

/- A small instrument for already closed theorem certificates. This does not
   extract arbitrary tactic states or change production verifier acceptance. -/
open Lean Elab Command Meta

namespace ProcedureContractAudit

private def tag (s : String) (xs : Array Json := #[]) : Json :=
  Json.arr (#[toJson s] ++ xs)

private def nameJson : Name → Json
  | .anonymous => tag "anonymous"
  | .str p s => tag "str" #[nameJson p, toJson s]
  | .num p n => tag "num" #[nameJson p, toJson n]

private def parameterIndex (n : Name) : List Name → Nat
  | [] => 0
  | p :: ps => if n == p then 0 else 1 + parameterIndex n ps

private def levelJson (params : List Name) : Level → Json
  | .zero => tag "zero"
  | .succ u => tag "succ" #[levelJson params u]
  | .max u v => tag "max" #[levelJson params u, levelJson params v]
  | .imax u v => tag "imax" #[levelJson params u, levelJson params v]
  | .param n => tag "param" #[toJson (parameterIndex n params)]
  | .mvar n => tag "UNSUPPORTED_LEVEL_MVAR" #[nameJson n.name]

/-- Alpha-canonical *syntax of an elaborated closed type*, not a claim that
    syntactically different types are semantically inequivalent. Let values,
    binder types/info, universe structure, constants, and dependencies remain. -/
private def exprJson (params : List Name) : Expr → Json
  | .bvar n => tag "bvar" #[toJson n]
  | .fvar n => tag "UNSUPPORTED_FVAR" #[nameJson n.name]
  | .mvar n => tag "UNSUPPORTED_MVAR" #[nameJson n.name]
  | .sort u => tag "sort" #[levelJson params u]
  | .const n us => tag "const" #[nameJson n, toJson (us.map (levelJson params))]
  | .app f a => tag "app" #[exprJson params f, exprJson params a]
  | .lam _ t b i => tag "lam" #[toJson (reprStr i), exprJson params t, exprJson params b]
  | .forallE _ t b i => tag "forall" #[toJson (reprStr i), exprJson params t, exprJson params b]
  | .letE _ t v b nd => tag "let" #[exprJson params t, exprJson params v, exprJson params b, toJson nd]
  | .lit l => tag "lit" #[toJson (reprStr l)]
  | .mdata _ b => exprJson params b
  | .proj n i b => tag "proj" #[nameJson n, toJson i, exprJson params b]

private def checkClosed (e : Expr) : CommandElabM Unit := do
  if e.hasFVar || e.hasMVar || e.hasLooseBVars then
    throwError "CONTRACT_AUDIT_NOT_CLOSED: free variables or metavariables"

elab "#audit_closed " id:ident : command => do
  let n ← liftCoreM <| realizeGlobalConstNoOverloadWithInfo id
  let ci ← getConstInfo n
  let .thmInfo thm := ci | throwError "CONTRACT_AUDIT_NOT_THEOREM"
  checkClosed thm.type
  checkClosed thm.value
  let env ← getEnv
  let (_, deps) := ((CollectAxioms.collect n).run env).run {}
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  for ax in deps.axioms do
    unless allowed.contains ax do
      throwError "CONTRACT_AUDIT_FORBIDDEN_AXIOM: {ax}"
  let used ← liftTermElabM <| lambdaTelescope thm.value fun xs body => do
    pure <| xs.mapIdx fun i x => Json.mkObj [
      ("binder_index", toJson i), ("used_in_body", toJson (body.containsFVar x.fvarId!))]
  let report := Json.mkObj [
    ("kind", toJson "closed_certificate"), ("name", toJson n.toString),
    ("interface", exprJson ci.levelParams ci.type),
    ("universe_parameter_count", toJson ci.numLevelParams),
    ("axioms", toJson (deps.axioms.map Name.toString)),
    ("proof_binder_usage", toJson used),
    ("direct_proof_constants", toJson (thm.value.getUsedConstants.map Name.toString))]
  logInfo m!"CONTRACT_JSON:{report.compress}"

elab "#compare_closed " lhs:ident rhs:ident : command => do
  let a ← getConstInfo (← liftCoreM <| realizeGlobalConstNoOverloadWithInfo lhs)
  let b ← getConstInfo (← liftCoreM <| realizeGlobalConstNoOverloadWithInfo rhs)
  checkClosed a.type
  checkClosed b.type
  unless a.levelParams.isEmpty && b.levelParams.isEmpty do
    throwError "CONTRACT_COMPARISON_UNSUPPORTED: polymorphic universe alignment"
  let defeq ← match Kernel.isDefEq (← getEnv) {} a.type b.type with
    | .ok result => pure result
    | .error _ => throwError "CONTRACT_COMPARISON_KERNEL_ERROR"
  let report := Json.mkObj [
    ("kind", toJson "interface_comparison"),
    ("lhs", toJson a.name.toString), ("rhs", toJson b.name.toString),
    ("kernel_definitionally_equal", toJson defeq),
    ("alpha_canonical_equal", toJson (exprJson a.levelParams a.type == exprJson b.levelParams b.type))]
  logInfo m!"CONTRACT_JSON:{report.compress}"

end ProcedureContractAudit
