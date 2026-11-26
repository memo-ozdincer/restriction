#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>
using Word=std::vector<int>;
using RNG=std::mt19937_64;
constexpr int N=4,G=12,MAXLEN=40,H=24,Q=32,K=6,B=32,D=16384,COMMON=300,PHASE=600,TAIL=300;
int src[G],dst[G];
std::vector<Word> words;
std::vector<std::vector<int>> alternatives;
int offset[4]={0,1,13,157};
int randint(RNG& r,int n){assert(n>0);return std::uniform_int_distribution<int>(0,n-1)(r);}
double uniform(RNG& r){return std::generate_canonical<double,53>(r);}
int wordid(const Word &w,int start,int length){
    int v=0;
    for(int i=0;i<length;i++)v=G*v+w[start+i];
    return offset[length]+v;
}
uint64_t permutation(const Word &w){
    uint64_t p=0;
    for(int x=0;x<16;x++){
        int y=x;
        for(int g:w)if((y>>src[g])&1)y^=1<<dst[g];
        p|=uint64_t(y)<<(4*x);
    }
    return p;
}
unsigned matrix(const Word &w){
    std::array<unsigned,4> row={1,2,4,8};
    for(int g:w)row[dst[g]]^=row[src[g]];
    return row[0]|(row[1]<<4)|(row[2]<<8)|(row[3]<<12);
}
void init(){
    int g=0;
    for(int s=0;s<N;s++)for(int d=0;d<N;d++)if(s!=d){src[g]=s;dst[g]=d;g++;}
    words.push_back({});
    for(int len=1;len<=3;len++){
        int limit=int(std::pow(G,len));
        for(int x=0;x<limit;x++){
            Word w(len);int t=x;
            for(int j=len-1;j>=0;j--){w[j]=t%G;t/=G;}
            assert(wordid(w,0,len)==int(words.size()));
            words.push_back(w);
        }
    }
    std::unordered_map<uint64_t,std::vector<int>> groups;
    for(int i=0;i<int(words.size());i++)groups[permutation(words[i])].push_back(i);
    alternatives.resize(words.size());
    long long count=0;
    for(int i=1;i<int(words.size());i++){
        for(int j:groups[permutation(words[i])])if(i!=j){
            assert(matrix(words[i])==matrix(words[j]));
            alternatives[i].push_back(j);count++;
        }
    }
    std::cerr<<"word_table "<<words.size()<<" equivalence_classes "<<groups.size()<<" rewrites "<<count<<"\n";
}
struct Edit{int pos=0,in=0,out=0;};
bool noop(const Edit&e){return e.in==0;}
int delta(const Edit&e){return int(words[e.out].size())-e.in;}
void apply_edit(Word&w,const Edit&e){
    if(noop(e))return;
    w.erase(w.begin()+e.pos,w.begin()+e.pos+e.in);
    w.insert(w.begin()+e.pos,words[e.out].begin(),words[e.out].end());
    assert(int(w.size())<=MAXLEN);
}
Edit propose(const Word&w,RNG&r){
    int L=w.size();
    int windows=L+std::max(0,L-1)+std::max(0,L-2);
    if(!windows)return {};
    int a=randint(r,windows),len=1;
    while(a>=L-len+1){a-=L-len+1;len++;}
    int id=wordid(w,a,len);
    const auto& alts=alternatives[id];
    if(alts.empty())return {};
    int out=alts[randint(r,alts.size())];
    if(L-len+int(words[out].size())>MAXLEN)return {};
    return {a,len,out};
}
using Feature=std::array<int,6>;
struct Hash{
    uint32_t h=2166136261u;
    int labels[4]={-1,-1,-1,-1},n=0;
    void num(int x){h=(h^uint32_t(x+1))*16777619u;}
    void gate(int g){
        int s=src[g],d=dst[g];
        if(labels[s]<0)labels[s]=n++;
        if(labels[d]<0)labels[d]=n++;
        num(labels[s]*4+labels[d]);
    }
};
int pattern(const Word&w,const Edit&e,int left,int right,int modulus,int base){
    Hash x;
    for(int i=std::max(0,e.pos-left);i<e.pos;i++)x.gate(w[i]);
    x.num(20);
    for(int i=0;i<e.in;i++)x.gate(w[e.pos+i]);
    x.num(21);
    for(int g:words[e.out])x.gate(g);
    x.num(22);
    for(int i=e.pos+e.in;i<std::min(int(w.size()),e.pos+e.in+right);i++)x.gate(w[i]);
    return base+(x.h%modulus);
}
Feature feats(const Word&w,const Edit&e){
    if(noop(e))return {16,17,18,19,20,21};
    int lens=e.in*4+words[e.out].size();
    return {lens,pattern(w,e,0,0,1024,32),
        pattern(w,e,2,0,2048,1056),pattern(w,e,0,2,2048,3104),
        pattern(w,e,2,2,8192,5152),13344+int(w.size())/4*16+lens};
}
struct Policy{
    std::vector<double> w,m,v;
    int updates=0;
    explicit Policy(int seed):w(D),m(D),v(D){
        RNG rng(seed);std::normal_distribution<double> norm(0,0.01);
        for(auto&x:w)x=norm(rng);
    }
    void step(const std::vector<double>&g){
        updates++;
        double b1=1-std::pow(.9,updates),b2=1-std::pow(.999,updates);
        for(int i=0;i<D;i++){
            m[i]=.9*m[i]+.1*g[i];v[i]=.999*v[i]+.001*g[i]*g[i];
            w[i]+=.01*(m[i]/b1)/(std::sqrt(v[i]/b2)+1e-8);
        }
    }
};
struct Episode{
    Word end;
    std::array<Edit,H> edits;
    int learned=0,reset=0,expansions=0,neutral=0,decrease=0,motifs=0,resetlen=0;
    bool valid=false;
};
Episode rollout(const Word& root,const Policy&pol,RNG&r,int prefix,double temp,bool ablate,double*grad=nullptr){
    Episode e;e.end=root;e.resetlen=root.size();
    std::array<int,H> lengths{};
    std::array<bool,H> eligible{};
    for(int t=0;t<H;t++){
        std::array<Edit,Q+1> cand{};
        for(int j=0;j<Q;j++)cand[j]=propose(e.end,r);
        int a=Q;
        if(t<prefix){
            std::array<int,Q+1> eligible{};int n=0;
            for(int j=0;j<=Q;j++)if(delta(cand[j])>=0)eligible[n++]=j;
            a=eligible[randint(r,n)];e.reset++;
        }else{
            e.learned++;
            std::array<Feature,Q+1> f{};
            std::array<double,Q+1> prob{};
            double max=-1e30;
            for(int j=0;j<=Q;j++){
                if(ablate&&!noop(cand[j])&&delta(cand[j])>=0){prob[j]=-1e30;continue;}
                f[j]=feats(e.end,cand[j]);double z=0;
                for(int i:f[j])z+=pol.w[i];
                prob[j]=z/temp;max=std::max(max,prob[j]);
            }
            double s=0;for(auto&v:prob){v=std::exp(v-max);s+=v;}
            double u=uniform(r)*s;
            for(int j=0;j<=Q;j++){
                u-=prob[j];if(u<0){a=j;break;}
            }
            if(grad){
                for(int j=0;j<=Q;j++)if(prob[j]>0){
                    double d=-prob[j]/s/temp;
                    for(int i:f[j])grad[i]+=d;
                }
                for(int i:f[a])grad[i]+=1/temp;
            }
            if(!noop(cand[a])){
                int d=delta(cand[a]);
                if(d<0)e.decrease++;
                if(d==0)e.neutral++;
                if(d>0)e.expansions++;
                eligible[t]=d>=0;
            }
        }
        e.edits[t]=cand[a];
        apply_edit(e.end,cand[a]);lengths[t]=e.end.size();
        if(t+1==prefix)e.resetlen=e.end.size();
    }
    int running=root.size();
    // Count voluntary nonshrinking edits that precede a new running minimum
    // within five further legal decisions. This is a temporal diagnostic only.
    for(int t=0;t<H;t++){
        running=std::min(running,lengths[t]);
        if(eligible[t]){
            for(int j=t+1;j<std::min(H,t+6);j++)if(lengths[j]<running){e.motifs++;break;}
        }
    }
    e.valid=matrix(root)==matrix(e.end);
    assert(e.valid);
    return e;
}
struct Pool{
    std::vector<Word> train,val,test,longtest;
    Pool(){
        RNG r(20261127);std::set<uint64_t> seen;
        auto generate=[&](int n,int len){
            std::vector<Word> out;
            while(int(out.size())<n){
                Word w(len);for(auto&x:w)x=randint(r,G);
                if(seen.insert(permutation(w)).second)out.push_back(w);
            }
            return out;
        };
        train=generate(256,24);val=generate(64,24);test=generate(128,24);longtest=generate(64,32);
    }
};
void wordjson(std::ostream &f,const Word&w){
    f<<"[";
    for(int j=0;j<int(w.size());j++){if(j)f<<",";f<<w[j];}
    f<<"]";
}
void dataset(const Pool&p,const std::string&path){
    std::ofstream f(path);
    auto write=[&](const char *name,const std::vector<Word>&v){
        f<<"\""<<name<<"\":[";
        for(size_t i=0;i<v.size();i++){if(i)f<<",";wordjson(f,v[i]);}
        f<<"]";
    };
    f<<"{";write("train",p.train);f<<",";write("validation",p.val);f<<",";write("test",p.test);f<<",";write("long_test",p.longtest);f<<"}\n";
}
struct Stats{
    long long episodes=0,learned=0,reset=0,finalcost=0,resetcost=0,improved=0,expansions=0,neutral=0,decrease=0,motifs=0,motifepisodes=0,verified=0;
    std::array<long long,MAXLEN+1> bycost{},motif_bycost{};
    void add(const Word&root,const Episode&e){
        episodes++;verified+=e.valid;learned+=e.learned;reset+=e.reset;
        finalcost+=e.end.size();resetcost+=e.resetlen;improved+=e.end.size()<root.size();
        expansions+=e.expansions;neutral+=e.neutral;decrease+=e.decrease;motifs+=e.motifs;motifepisodes+=e.motifs>0;
        bycost[e.end.size()]++;motif_bycost[e.end.size()]+=e.motifs>0;
    }
    void json(std::ostream&f)const{
        f<<"{\"episodes\":"<<episodes<<",\"learned\":"<<learned<<",\"reset\":"<<reset
        <<",\"proposals\":"<<(learned+reset)*Q<<",\"verified\":"<<verified<<",\"finalcost\":"<<finalcost
        <<",\"resetcost\":"<<resetcost<<",\"improved\":"<<improved<<",\"expanding\":"<<expansions
        <<",\"neutral\":"<<neutral<<",\"decrease\":"<<decrease<<",\"motifs\":"<<motifs
        <<",\"motifepisodes\":"<<motifepisodes<<",\"mean_cost\":"<<double(finalcost)/episodes
        <<",\"improved_rate\":"<<double(improved)/episodes<<",\"bycost\":[";
        for(int j=0;j<=MAXLEN;j++){if(j)f<<",";f<<bycost[j];}
        f<<"],\"motif_bycost\":[";
        for(int j=0;j<=MAXLEN;j++){if(j)f<<",";f<<motif_bycost[j];}
        f<<"]}";
    }
};
Stats evaluate(const std::vector<Word>&pool,const std::string&split,const std::string&label,const Policy&p,int draws,int prefix,bool ablate,std::ostream* trace){
    Stats stats;
    // Each arm uses the identical RNG seed for each root/replicate. State
    // divergence can change subsequent proposal draws.
    for(int j=0;j<int(pool.size());j++)for(int k=0;k<draws;k++){
        RNG r(10000000ULL + 9973*j +113*k + (split=="long_test"?4000000:0));
        const auto&root=pool[j];
        Episode e=rollout(root,p,r,prefix,1.,ablate);
        stats.add(root,e);
        if(trace&&k==0){
            *trace<<"{\"split\":\""<<split<<"\",\"label\":\""<<label<<"\",\"root_id\":"<<j<<",\"root\":";
            wordjson(*trace,root);*trace<<",\"prefix\":"<<prefix<<",\"ablate\":"<<(ablate?"true":"false")<<",\"edits\":[";
            for(int t=0;t<H;t++){
                if(t)*trace<<",";
                const auto&a=e.edits[t];*trace<<"["<<a.pos<<","<<a.in<<",";wordjson(*trace,words[a.out]);*trace<<"]";
            }
            *trace<<"],\"end\":";wordjson(*trace,e.end);
            *trace<<",\"motifs\":"<<e.motifs<<"}\n";
        }
    }
    return stats;
}
void train(Policy&p,const Pool&pool,RNG&r,int steps,int prefix,double temp,Stats& stats){
    std::vector<double> scores(B*D),g(D),returns(B);
    for(int s=0;s<steps;s++){
        const Word&root=pool.train[randint(r,pool.train.size())];
        std::fill(scores.begin(),scores.end(),0.);
        double mean=0;
        for(int b=0;b<B;b++){
            Episode e=rollout(root,p,r,prefix,temp,false,&scores[b*D]);
            stats.add(root,e);
            returns[b]=1.+double(MAXLEN-e.end.size())/MAXLEN;
            mean+=returns[b]/B;
        }
        double var=0;for(double v:returns)var+=(v-mean)*(v-mean)/B;
        double sd=std::sqrt(var)+1e-8;
        std::fill(g.begin(),g.end(),0.);
        for(int b=0;b<B;b++){
            double a=(returns[b]-mean)/(sd*B);
            for(int j=0;j<D;j++)g[j]+=a*scores[b*D+j];
        }
        p.step(g);
    }
}
int main(int argc,char**argv){
    if(argc<3){std::cerr<<"usage: run SEED PREFIX_PATH [smoke]\n";return 1;}
    int seed=std::stoi(argv[1]);std::string path=argv[2];bool smoke=argc>3;
    init();Pool pool;
    dataset(pool,path+".dataset.json");
    Policy p(seed);RNG r(seed+9000);
    std::ofstream f(path+".json");std::ofstream trace(path+".traces.jsonl");
    f<<std::setprecision(12)<<"{\"seed\":"<<seed<<",\"smoke\":"<<(smoke?"true":"false")<<",\"common\":{";
    int common=smoke?10:COMMON,phase=smoke?10:PHASE,tail=smoke?5:TAIL;
    Stats init=evaluate(pool.val,"validation","init",p,4,0,false,nullptr);f<<"\"initial\":";init.json(f);
    Stats commontrain;train(p,pool,r,common,0,1.,commontrain);f<<",\"training\":";commontrain.json(f);
    Stats val=evaluate(pool.val,"validation","checkpoint",p,4,0,false,nullptr);f<<",\"validation\":";val.json(f);
    bool competent=val.improved>=.8*val.episodes && double(val.finalcost)/val.episodes<=.8*24;
    f<<",\"competent\":"<<(competent?"true":"false")<<",\"test\":";
    auto pre=evaluate(pool.test,"test","common",p,8,0,false,&trace);pre.json(f);
    f<<",\"test_prefix_frozen\":";
    auto frozen=evaluate(pool.test,"test","frozen_prefix",p,8,K,false,&trace);frozen.json(f);
    f<<"}";
    std::cerr<<"seed "<<seed<<" baseline mean "<<double(val.finalcost)/val.episodes<<" improved "<<double(val.improved)/val.episodes<<" competent "<<competent<<"\n";
    if(!competent&&!smoke){f<<",\"arms\":[]}\n";return 0;}
    f<<",\"arms\":[";
    for(int arm=0;arm<3;arm++){
        std::string name=arm==0?"ordinary":arm==1?"exposure":"entropy";
        auto q=p;auto branch_rng=r;
        Stats first,last;
        train(q,pool,branch_rng,phase,arm==1?K:0,arm==2?2.:1.,first);
        auto phase_eval=evaluate(pool.test,"test",name+"_phase",q,8,0,false,&trace);
        train(q,pool,branch_rng,tail,0,1.,last);
        auto test=evaluate(pool.test,"test",name+"_final",q,8,0,false,&trace);
        auto ablate=evaluate(pool.test,"test",name+"_ablated",q,8,0,true,&trace);
        auto longtest=evaluate(pool.longtest,"long_test",name+"_long",q,8,0,false,&trace);
        if(arm)f<<",";
        f<<"{\"name\":\""<<name<<"\",\"phase_training\":";first.json(f);
        f<<",\"phase_eval\":";phase_eval.json(f);
        f<<",\"tail_training\":";last.json(f);
        f<<",\"test\":";test.json(f);
        f<<",\"ablated\":";ablate.json(f);
        f<<",\"long_test\":";longtest.json(f);
        f<<",\"weights\":[";
        for(int i=0;i<D;i++){if(i)f<<",";f<<q.w[i];}f<<"]}";
        f.flush();
        std::cerr<<"seed "<<seed<<" arm "<<name<<" test cost "<<double(test.finalcost)/test.episodes<<" motif fraction "<<double(test.motifepisodes)/test.episodes<<"\n";
    }
    f<<"]}\n";
}
