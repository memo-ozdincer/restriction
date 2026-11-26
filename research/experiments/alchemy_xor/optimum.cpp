#include <cstdint>
#include <iostream>
#include <fstream>
#include <unordered_set>
#include <cassert>
using U=uint32_t;
constexpr U bit(int i){return U(1)<<i;}
constexpr U ROOT=bit(1)|bit(2)|bit(4)|bit(8)|bit(16);
int pc(U x){return __builtin_popcount(x);}
bool examine(U s,U t,int left,std::unordered_set<U>&failed){
 if((s&t)==t)return true;
 int missing=pc(t&~s);
 if(missing>left || failed.count(s))return false;
 U next=0;
 for(int i=1;i<32;i++)if(s&bit(i))for(int j=i+1;j<32;j++)if(s&bit(j))next|=bit(i^j);
 next&=~s;
 if(missing==left)next&=t; // All remaining steps must create target wires.
 for(U choices : {next&t,next&~t})while(choices){int z=__builtin_ctz(choices);choices&=choices-1;if(examine(s|bit(z),t,left-1,failed))return true;}
 failed.insert(s);return false;
}
int main(int argc,char**argv){
 assert(argc==2);std::ifstream f(argv[1]);U t;int i=0;
 while(f>>t){if(i>=384){int k=pc(t&~ROOT);for(;k<=20;k++){std::unordered_set<U> seen;if(examine(ROOT,t,k,seen))break;}assert(k<=20);std::cout<<i<<","<<t<<","<<k<<"\n";}i++;}
}
