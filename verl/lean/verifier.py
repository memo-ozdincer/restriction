from typing import List

import os
import re
import sys
import time

_prover_root = os.environ.get(
    "DEEPSEEK_PROVER_ROOT", "/scratch/memoozd/rl/DeepSeek-Prover-V1.5"
)
_verifier_memory_limit_gb = int(os.environ.get("DEEPSEEK_VERIFIER_MEMORY_LIMIT_GB", "10"))
if _prover_root not in sys.path:
    sys.path.insert(0, _prover_root)
from prover.lean.verifier import Lean4ServerScheduler

prompt = r'''Complete the following Lean 4 code:

```lean4
'''

code_prefix = r'''import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

'''

def verify_with_deepseek_verifier(
        full_proofs: List[str],
        theorem_statements: List[str], 
        contexts: List[str], 
        max_workers: int = 16,
        penalize_extra_text: bool = False,
    ):

    assert len(full_proofs) % len(theorem_statements) == 0
    assert len(theorem_statements) == len(contexts)

    num_problems = len(theorem_statements)
    num_samples_per_problem = len(full_proofs) // num_problems

    # first we assemble the proof code files
    # which consists of the context, statement, and proof
    # we will use the context hardcoded in the template
    code_files = []
    after_code_texts = []  # New list to store text after the code blocks
    parse_times = []
    parse_failures = []
    num_parse_fails = 0
    for i in range(len(full_proofs)):
        parse_start = time.perf_counter()
        theorem_statement = theorem_statements[i // num_samples_per_problem]
        proof_body = full_proofs[i]
        code_file = prompt + code_prefix + theorem_statement + proof_body
        # try to parse the code file
        try:
            # Extract the code part
            code_match = re.search(r'```lean4\n(.*?)\n```', code_file, re.DOTALL)
            if code_match:
                code_file_parsed = code_match.group(1)
                code_files.append(code_file_parsed)
                
                # Extract everything after the closing ```
                end_pos = code_match.end()
                after_code_text = code_file[end_pos:].strip()
                after_code_texts.append(after_code_text)
                parse_failures.append(False)
            else:
                raise Exception("No code block found")
        except Exception as e:
            # this should result in a verification failure
            num_parse_fails += 1
            code_files.append("failed to parse")
            after_code_texts.append("")  # Add empty string for failed parses
            parse_failures.append(True)
        finally:
            parse_times.append(time.perf_counter() - parse_start)

    print(f"[VERIFIER] {num_parse_fails} parse failures")
    # print(code_files[0])
    # print(code_files[-1])

    lean4_scheduler = Lean4ServerScheduler(
        max_concurrent_requests=max_workers, 
        timeout=300, 
        memory_limit=_verifier_memory_limit_gb,
        name='verifier'
    )

    request_id_list = lean4_scheduler.submit_all_request(code_files)
    outputs_list = lean4_scheduler.get_all_request_outputs(request_id_list)
    lean4_scheduler.close()

    # print(outputs_list[0])
    # print(outputs_list[-1])

    final_outputs = []
    for i in range(num_problems):
        outputs = outputs_list[i * num_samples_per_problem:(i + 1) * num_samples_per_problem]
        correct = [output["complete"] for output in outputs]
        penalized_extra_text = [False] * num_samples_per_problem

        if penalize_extra_text:
            # extra_text = after_code_texts[i * num_samples_per_problem:(i + 1) * num_samples_per_problem]
            # has_extra_text = [len(text.strip()) > 0 for text in extra_text]
            text = full_proofs[i * num_samples_per_problem:(i + 1) * num_samples_per_problem]
            has_extra_text = [not t.strip().endswith("```") for t in text]
            for j in range(num_samples_per_problem):
                if has_extra_text[j]:
                    correct[j] = False
                    penalized_extra_text[j] = True
                    print(f"[VERIFIER] Penalized extra text for sample {j}")
                    print(text[j])

        candidate_results = []
        offset = i * num_samples_per_problem
        for j, output in enumerate(outputs):
            system_error = str(output.get("system_errors") or "")
            error_lower = system_error.lower()
            timed_out = "timeoutexpired" in error_lower or "timed out after" in error_lower
            if parse_failures[offset + j]:
                failure_class = "proof_parse_failure"
            elif penalized_extra_text[j]:
                failure_class = "extra_text_penalty"
            elif system_error:
                failure_class = "timeout" if timed_out else "verifier_exception"
            elif not output.get("complete", False):
                failure_class = "lean_rejected"
            else:
                failure_class = None
            candidate_results.append({
                "verdict": bool(correct[j]),
                "lean_complete": bool(output.get("complete", False)),
                "parse_time_seconds": parse_times[offset + j],
                "queue_wait_time_seconds": output.get("queue_wait_time"),
                "verification_time_seconds": output.get("verify_time"),
                "worker_id": output.get("worker_id"),
                "failure_class": failure_class,
                "timed_out": timed_out,
                "verifier_error": system_error[-4096:] or None,
            })
        
        success_indices = [i for i, s in enumerate(correct) if s]
        incomplete = [not output["complete"] for output in outputs]
        final_outputs.append(dict(
            success = any(correct),
            num_success = sum(correct),
            success_indices = success_indices,
            num_errors = sum(incomplete),
            msg = "Search successful" if any(correct) else f"Search ended with {sum(incomplete)} errors",
            candidate_results = candidate_results,
        ))
    
    return final_outputs
