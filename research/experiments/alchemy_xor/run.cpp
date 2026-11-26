#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>
using namespace std;
using U=uint32_t;
constexpr int H=20,F=17,B=64,PRE=1200,POST=1800;
constexpr U bit(int i){return U(1)<<i;}
constexpr U ROOT=bit(1)|bit(2)|bit(4)|bit(8)|bit(16);
int pc(U x){return __builtin_popcount(x);}
int randn(mt19937 &r,int n){return uniform_int_distribution<int>(0,n-1)(r);}
double unif(mt19937 &r){return generate_canonical<double,53>(r);}
int rank5(vector<int> x){int rank=0;for(int j=4;j>=0;j--){int i=rank;while(i<5&&!(x[i]&(1<<j)))i++;if(i==5)continue;swap(x[rank],x[i]);for(int k=rank+1;k<5;k++)if(x[k]&(1<<j))x[k]^=x[rank];rank++;}return rank;}
vector<U> maps(){mt19937 r(20261127);vector<U> out;set<U> seen;while(out.size()<640){vector<int>x;U t=0;while(x.size()<5){int y=randn(r,31)+1;if(!(t&bit(y))){t|=bit(y);x.push_back(y);}}if(rank5(x)==5&&seen.insert(t).second)out.push_back(t);}return out;}
using V=array<double,F>;
struct Model{V w{},m{},v{};int step=0;void update(V g){step++;for(int i=0;i<F;i++){m[i]=.9*m[i]+.1*g[i];v[i]=.999*v[i]+.001*g[i]*g[i];w[i]+=.02*(m[i]/(1-pow(.9,step)))/(sqrt(v[i]/(1-pow(.999,step)))+1e-8);}}};
struct Gate{int z,a,b;};
struct Action{int z;vector<pair<int,int>> pairs;V f{};double p=0;};
vector<Action> actions(U s,U t,bool features=true){
 vector<Action> a(32);for(int i=1;i<32;i++)a[i].z=i;
 for(int i=1;i<32;i++)if(s&bit(i))for(int j=i+1;j<32;j++)if(s&bit(j)){int z=i^j;if(!(s&bit(z)))a[z].pairs.emplace_back(i,j);}
 array<bool,32> reachable{};for(int i=1;i<32;i++)reachable[i]=!a[i].pairs.empty();
 vector<Action> out;for(int z=1;z<32;z++)if(!a[z].pairs.empty()){
  auto &x=a[z];if(features){x.f[0]=!!(t&bit(z));x.f[1]=pc(z)/5.;x.f[2]=x.pairs.size()/15.;
   int unlock=0;for(int i=1;i<32;i++){int d=pc(i^z);if(s&bit(i))x.f[3+d]+=1./10;
    if((t&bit(i))&&!(s&bit(i))) {x.f[9+d]+=1./5;if(i!=z&&(s&bit(z^i))&&!reachable[i])unlock++;}}
   x.f[15]=unlock/5.;x.f[16]=x.f[0]*pc(s)/31.;
  }out.push_back(std::move(x));
 }return out;
}
struct Ep{double reward=0;int len=0,calls=0,resets=0,rejected=0,shared=0,cancel=0;bool ok=false;V score{};vector<Gate> gates;};
Ep episode(const Model&m,U t,mt19937&r,mt19937&rr,int mode,bool grad){
 Ep e;U s=ROOT;int prefix=mode?randn(rr,9):0;
 while(e.len<H && (s&t)!=t){
  bool reset=e.len<prefix;bool random=reset&&mode==1;auto ac=actions(s,t,!random);assert(!ac.empty());int k=0;
  if(random) { // Uniform over legal operand pairs, not unique result masks.
   int total=0;for(auto &a:ac)total+=a.pairs.size();int q=randn(rr,total);
   while(q>=int(ac[k].pairs.size()))q-=ac[k++].pairs.size();
  }else{
   double mx=-1e100;for(auto&a:ac){for(int i=0;i<F;i++)a.p+=m.w[i]*a.f[i];mx=max(mx,a.p);}double sum=0;for(auto&a:ac)sum+=(a.p=exp(a.p-mx));
   double q=unif(reset?rr:r)*sum;while(k+1<int(ac.size()) && q>=ac[k].p)q-=ac[k++].p;
   e.calls++;
   if(grad&&!reset){for(int i=0;i<F;i++)e.score[i]+=ac[k].f[i];for(auto&a:ac) for(int i=0;i<F;i++)e.score[i]-=a.p/sum*a.f[i];}
  }
  auto &a=ac[k];auto p=a.pairs[randn(reset?rr:r,a.pairs.size())];e.gates.push_back({a.z,p.first,p.second});s|=bit(a.z);e.len++;e.resets+=reset;
 }
 e.ok=(s&t)==t;e.reward=e.ok?1+(H-e.len)/double(H):0;
 if(mode&&e.ok&&e.len<=prefix){e.rejected=1;e.score={};}
 // Independent gate replay using concrete truth vectors, not symbolic masks.
 uint32_t vals[32]={};U avail=ROOT;for(int i=0;i<5;i++){uint32_t val=0;for(int b=0;b<32;b++)if(b&(1<<i))val|=bit(b);vals[1<<i]=val;}
 array<U,32> anc{};
 for(auto g:e.gates){assert((avail&bit(g.a))&&(avail&bit(g.b))&&!(avail&bit(g.z)));vals[g.z]=vals[g.a]^vals[g.b];uint32_t expected=0;for(int b=0;b<32;b++)if(pc(b&g.z)&1)expected|=bit(b);assert(vals[g.z]==expected);avail|=bit(g.z);anc[g.z]=anc[g.a]|anc[g.b]|bit(g.z);}
 assert(((avail&t)==t)==e.ok);
 if(e.ok){for(auto g:e.gates)if(!(t&bit(g.z))){int usage=0;bool cancel=false;for(int j=1;j<32;j++)if((t&bit(j))&&(anc[j]&bit(g.z))){usage++;cancel|=bool(g.z&~j);}e.shared+=(usage>=2);e.cancel+=cancel;}}
 return e;
}
struct Stats{long long n=0,ok=0,calls=0,gates=0,reset=0,rejects=0;double reward=0,cost=0,share=0,cancel=0;void add(Ep&e){n++;ok+=e.ok;reward+=e.reward;calls+=e.calls;gates+=e.len;reset+=e.resets;rejects+=e.rejected;if(e.ok){cost+=e.len;share+=e.shared;cancel+=e.cancel;}}};
void write_stats(ostream&o,Stats s){o<<"{\"n\":"<<s.n<<",\"ok\":"<<s.ok<<",\"calls\":"<<s.calls<<",\"gates\":"<<s.gates<<",\"resets\":"<<s.reset<<",\"rejected\":"<<s.rejects<<",\"reward\":"<<s.reward/s.n<<",\"conditional_cost\":"<<s.cost/max(1LL,s.ok)<<",\"shared\":"<<s.share/max(1LL,s.ok)<<",\"cancel\":"<<s.cancel/max(1LL,s.ok)<<"}";}
Stats evaluate(const Model&m,const vector<U>&tasks,int begin,int end,int reps,int seed,ostream*traces=nullptr){
 mt19937 r(seed),rr(seed+1);Stats s;for(int i=begin;i<end;i++)for(int j=0;j<reps;j++){Ep e=episode(m,tasks[i],r,rr,0,false);s.add(e);if(traces){*traces<<i<<","<<j<<","<<tasks[i]<<","<<e.ok<<","<<e.len<<","<<e.shared<<","<<e.cancel<<",";for(auto g:e.gates)*traces<<g.z<<":"<<g.a<<":"<<g.b<<";";*traces<<"\n";}}return s;
}
Stats train(Model&m,const vector<U>&tasks,int seed,int mode,int updates,ostream&log){
 mt19937 r(seed+100),rr(seed+200),tr(seed+300);Stats total;
 for(int step=0;step<updates;step++){
  array<Ep,B> batch;double mean=0;int count=0;for(auto&e:batch){e=episode(m,tasks[randn(tr,256)],r,rr,mode,true);total.add(e);if(!e.rejected){mean+=e.reward;count++;}}
  V g{};if(count){mean/=count;for(auto&e:batch)if(!e.rejected)for(int i=0;i<F;i++)g[i]+=e.score[i]*(e.reward-mean)/count;m.update(g);}
  if((step+1)%300==0){auto ev=evaluate(m,tasks,256,384,2,seed+400);log<<"{\"update\":"<<step+1<<",\"validation\":";write_stats(log,ev);log<<",\"training\":";write_stats(log,total);log<<"}\n";log.flush();}
 }return total;
}
void write_model(ostream&o,Model&m){o<<"[";for(int i=0;i<F;i++){if(i)o<<",";o<<m.w[i];}o<<"]";}
int main(int argc,char**argv){
 if(argc<3)return 1;int seed=stoi(argv[1]);string out=argv[2];bool smoke=argc>3;auto tasks=maps();
 ofstream mapf(out+"/maps-"+to_string(seed)+".txt");for(U t:tasks)mapf<<t<<"\n";
 Model common;mt19937 init(seed);for(auto&w:common.w)w=normal_distribution<double>(0,.02)(init);
 ofstream res(out+"/seed-"+to_string(seed)+".json");res<<setprecision(17);
 auto v0=evaluate(common,tasks,256,384,4,seed+501);ofstream prelog(out+"/pre-"+to_string(seed)+".jsonl");
 Stats pre=train(common,tasks,seed,0,smoke?3:PRE,prelog);auto val=evaluate(common,tasks,256,384,4,seed+501);
 bool competent=val.ok>=.8*val.n && val.reward/val.n>v0.reward/v0.n;
 ofstream tr(out+"/trace-"+to_string(seed)+"-common.csv");auto baseline=evaluate(common,tasks,384,640,8,seed+601,&tr);
 res<<"{\"seed\":"<<seed<<",\"competent\":"<<competent<<",\"init_validation\":";write_stats(res,v0);res<<",\"common_validation\":";write_stats(res,val);res<<",\"common_heldout\":";write_stats(res,baseline);res<<",\"common_training\":";write_stats(res,pre);res<<",\"common_weights\":";write_model(res,common);res<<",\"arms\":[";
 if(competent||smoke)for(int mode=0;mode<3;mode++){Model m=common;ofstream lg(out+"/arm-"+to_string(seed)+"-"+to_string(mode)+".jsonl");Stats train_s=train(m,tasks,seed+10000,mode,smoke?3:POST,lg);ofstream traces(out+"/trace-"+to_string(seed)+"-"+to_string(mode)+".csv");auto held=evaluate(m,tasks,384,640,8,seed+601,&traces);if(mode)res<<",";res<<"{\"mode\":"<<mode<<",\"train\":";write_stats(res,train_s);res<<",\"heldout\":";write_stats(res,held);res<<",\"weights\":";write_model(res,m);res<<"}";res.flush();}
 res<<"]}\n";cout<<"seed "<<seed<<" competence "<<competent<<" validation "<<val.ok<<"/"<<val.n<<endl;
}
