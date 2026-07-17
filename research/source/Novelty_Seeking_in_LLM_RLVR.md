# Novelty Seeking in LLM RLVR

##### [**Undermind**](https://undermind.ai)

---

**Research Goal:** Find research papers on large language models trained or optimized with reinforcement learning using automatically verifiable rewards, where the method is intended to make the search process more likely to discover novel, diverse, unexpected, or otherwise interesting valid solutions. Include work applied to mathematical theorem proving or proof generation, games, code or program synthesis, and other environments where outputs can be checked automatically. Consider both methods that make novelty, diversity, exploration, or quality-diversity an explicit objective and methods that induce this behavior indirectly through mechanisms such as populations, self-play, adversarial or diverse task generation, alternative solution trajectories, or other search strategies. Prioritize papers that introduce or empirically evaluate a concrete mechanism for improving the discovery of interesting solutions, rather than papers that only use standard RLVR to optimize correctness or benchmark performance.

*Found 72 papers · July 17, 2026 · Estimated coverage of relevant papers: 78%*

## Summary of Results

Outcome-only RLVR commonly sharpens probability around already likely correct trajectories, degrading pass@k and suppressing rare valid reasoning; the clearest direct remedies reward underrepresented correct outputs or optimize the sampled set rather than independent rollouts \[3, 2, 10, 1\].

#### Three intervention levels

- **Redistribute credit among valid solutions.** Unlikeliness reward counters GRPO’s rank bias in formal proving \[3\]; outcome-frequency/UCB bonuses and within-batch repetition penalties preserve answer-level coverage \[2\]. Representation-, semantic-, or set-kernel diversity bonuses target trajectory-level distinctness \[1, 7, 9\], while mass-covering divergence regularization preserves support inherited from the base policy \[17\].
- **Optimize collective success, not isolated pass@1.** Pass@k objectives assign reward by a rollout’s marginal contribution to group success, making diversity instrumentally valuable and helping on problems where conventional RL stalls \[10, 12\]. For code, direct anti-redundancy rewards and coordinated high-level strategy planning extend this logic to implementation and algorithmic diversity \[35, 34\].
- **Expand the task distribution.** Self-play systems make novelty operational through a proposer generating tasks near the solver’s capability frontier: conjecture–prove loops in Lean/Isabelle \[6\], code-executor-grounded zero-data curricula \[5\], and formally verified code proposal \[20\]. Hierarchical proof decomposition supplies a complementary novelty source—verified intermediate lemmas enter replay—even when the target theorem remains unsolved \[4\].

A recurring distinction is **within-prompt solution coverage** versus **open-ended problem discovery**: the former is measured by diversity/pass@k; the latter requires difficulty-calibrated task generation and a reliable verifier. Evolutionary program search couples both, using evaluated discoveries to update the LLM search operator \[24, 25\], with FunSearch providing the influential verifier-guided discovery baseline \[67\].

## Paper Catalog (72 papers)

|  | Year | Cit/yr | Title | Authors | Journal |
|---:|:--:|:--:|:---|:---|:---|
| 1 | 2025 | 17 | Representation-Based Exploration for Language Models: From Test-Time to Post-Training ([link](https://doi.org/10.48550/arXiv.2510.11686)) | Jens Tuyls, Dylan J. Foster, Akshay Krishnamurthy, and Jordan T. Ash | ArXiv |
| 2 | 2025 | 88 | Outcome-based Exploration for LLM Reasoning ([link](https://doi.org/10.48550/arXiv.2509.06941)) | Yuda Song, Julia Kempe, and Rémi Munos | ArXiv |
| 3 | 2025 | 67 | Rewarding the Unlikely: Lifting GRPO Beyond Distribution Sharpening ([link](https://doi.org/10.48550/arXiv.2506.02355)) | Andre He, Daniel Fried, and S. Welleck | Conference on Empirical Methods in Natural Language Processing |
| 4 | 2024 | 11 | Formal Theorem Proving by Rewarding LLMs to Decompose Proofs Hierarchically ([link](https://doi.org/10.48550/arXiv.2411.01829)) | Kefan Dong, Arvind V. Mahankali, and Tengyu Ma | ArXiv |
| 5 | 2025 | 224 | Absolute Zero: Reinforced Self-play Reasoning with Zero Data ([link](https://doi.org/10.48550/arXiv.2505.03335)) | Andrew Zhao et al. | ArXiv |
| 6 | 2025 | 50 | STP: Self-play LLM Theorem Provers with Iterative Conjecturing and Proving ([link](https://doi.org/10.48550/arXiv.2502.00212)) | Kefan Dong and Tengyu Ma | ArXiv |
| 7 | 2025 | 75 | Jointly Reinforcing Diversity and Quality in Language Model Generations ([link](https://doi.org/10.48550/arXiv.2509.02534)) | Tianjian Li et al. | ArXiv |
| 8 | 2025 | 34 | Diversity-Aware Policy Optimization for Large Language Model Reasoning ([link](https://doi.org/10.48550/arXiv.2505.23433)) | Jian Yao, Ran Cheng, Xingyu Wu, Jibin Wu, and Kay Chen Tan | ArXiv |
| 9 | 2026 | 4.0 | SetPO: Set-Level Policy Optimization for Diversity-Preserving LLM Reasoning ([link](https://doi.org/10.48550/arXiv.2602.01062)) | Chenyi Li et al. | ArXiv |
| 10 | 2025 | 55 | Pass@K Policy Optimization: Solving Harder Reinforcement Learning Problems ([link](https://doi.org/10.48550/arXiv.2505.15201)) | Christian J. Walder and Deep Karkhanis | ArXiv |
| 11 | 2025 | 26 | Diversity-Incentivized Exploration for Versatile Reasoning ([link](https://doi.org/10.48550/arXiv.2509.26209)) | Zican Hu et al. | ArXiv |
| 12 | 2025 | 129 | Pass@k Training for Adaptively Balancing Exploration and Exploitation of Large Reasoning Models ([link](https://doi.org/10.48550/arXiv.2508.10751)) | Zhipeng Chen et al. | ArXiv |
| 13 | 2026 |  | ExTra: Exploratory Trajectory Optimization for Language Model Reinforcement Learning ([link](https://www.semanticscholar.org/paper/ba42dbb6e6ac459e0f1ffbdfe0b1e3b65c3eb638)) | Wenyang Hu et al. |  |
| 14 | 2026 | 14 | Rewarding the Rare: Uniqueness-Aware RL for Creative Problem Solving in LLMs ([link](https://doi.org/10.48550/arXiv.2601.08763)) | Zhiyuan Hu et al. | ArXiv |
| 15 | 2025 | 53 | Evolving Language Models without Labels: Majority Drives Selection, Novelty Promotes Variation ([link](https://doi.org/10.48550/arXiv.2509.15194)) | Yujun Zhou et al. | ArXiv |
| 16 | 2025 | 16 | Beyond the Sampled Token: Preserving Candidate Support in RLVR ([link](https://www.semanticscholar.org/paper/4af03e3796c0767104581ca8d56f01824d3e9e52)) | Ruotian Peng, Yi Ren, Zhouliang Yu, Weiyang Liu, and Yandong Wen |  |
| 17 | 2025 | 36 | The Choice of Divergence: A Neglected Key to Mitigating Diversity Collapse in Reinforcement Learning with Verifiable Reward ([link](https://doi.org/10.48550/arXiv.2509.07430)) | Long Li et al. | ArXiv |
| 18 | 2025 | 253 | Reasoning with Exploration: An Entropy Perspective ([link](https://doi.org/10.48550/arXiv.2506.14758)) | Daixuan Cheng et al. | AAAI Conference on Artificial Intelligence |
| 19 | 2024 | 23 | Learning Formal Mathematics From Intrinsic Motivation ([link](https://doi.org/10.48550/arXiv.2407.00695)) | Gabriel Poesia, David Broman, Nick Haber, and Noah D. Goodman | ArXiv |
| 20 | 2025 | 7.0 | Propose, Solve, Verify: Self-Play Through Formal Verification ([link](https://doi.org/10.48550/arXiv.2512.18160)) | Alex Wilf et al. | ArXiv |
| 21 | 2025 | 6.6 | GAR: Generative Adversarial Reinforcement Learning for Formal Theorem Proving ([link](https://doi.org/10.48550/arXiv.2510.11769)) | Ruida Wang, Jiarui Yao, Rui Pan, Shizhe Diao, and Tong Zhang | ArXiv |
| 22 | 2026 |  | ANCORA: Learning to Question via Manifold-Anchored Self-Play for Verifiable Reasoning ([link](https://doi.org/10.48550/arXiv.2604.27644)) | Chengcao Yang and Jun Chen | ArXiv |
| 23 | 2026 |  | PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play ([link](https://www.semanticscholar.org/paper/4fe61ff9df9714770be1fafa688b4591d07b807a)) | Roger Creus Castanyer et al. |  |
| 24 | 2025 | 35 | Algorithm Discovery With LLMs: Evolutionary Search Meets Reinforcement Learning ([link](https://doi.org/10.48550/arXiv.2504.05108)) | Anja Surina et al. | ArXiv |
| 25 | 2025 | 22 | CALM: Co-evolution of Algorithms and Language Model for Automatic Heuristic Design ([link](https://doi.org/10.48550/arXiv.2505.12285)) | Ziyao Huang, Weiwei Wu, Kui Wu, Jianping Wang, and Wei-Bin Lee | ArXiv |
| 26 | 2026 | 4.0 | Poly-EPO: Training Exploratory Reasoning Models ([link](https://doi.org/10.48550/arXiv.2604.17654)) | Ifdita Hasan Orney et al. | ArXiv |
| 27 | 2026 |  | When RL Suppresses Its Own Vocabulary: Recovering Reasoning Diversity in Puzzle-to-Math Transfer ([link](https://www.semanticscholar.org/paper/d8d6ff9edbf7a975253115e28a45e98701c5c2d8)) | Mayug Maniparambil, Arjun Karuvally, Terrence J. Sejnowski, and Fergal Reid |  |
| 28 | 2026 |  | Breaking $`\textit{Winner-Takes-All}`$: Cooperative Policy Optimization Improves Diverse LLM Reasoning ([link](https://www.semanticscholar.org/paper/75222439892a2fe50d3d0390795203364cc34040)) | Haoxuan Chen, Tianming Liang, Wei-Shi Zheng, and Jian-Fang Hu |  |
| 29 | 2025 | 11 | Random Policy Valuation is Enough for LLM Reasoning with Verifiable Rewards ([link](https://doi.org/10.48550/arXiv.2509.24981)) | Haoran He et al. | ArXiv |
| 30 | 2025 | 20 | Differential Smoothing Mitigates Sharpening and Improves LLM Reasoning ([link](https://doi.org/10.48550/arXiv.2511.19942)) | Jingchu Gai, Guanning Zeng, Huaqing Zhang, and Aditi Raghunathan | ArXiv |
| 31 | 2025 | 41 | Unlocking Exploration in RLVR: Uncertainty-aware Advantage Shaping for Deeper Reasoning ([link](https://doi.org/10.48550/arXiv.2510.10649)) | Can Xie et al. | ArXiv |
| 32 | 2026 |  | Uniform-Correct Policy Optimization: Breaking RLVR’s Indifference to Diversity ([link](https://www.semanticscholar.org/paper/e3b2d3d1a8cf1a6f74748455df21dfc955fefea9)) | Anamika Lochab, Bolian Li, and Ruqi Zhang |  |
| 33 | 2025 | 19 | Improving RL Exploration for LLM Reasoning through Retrospective Replay ([link](https://doi.org/10.48550/arXiv.2504.14363)) | Shihan Dou et al. | ArXiv |
| 34 | 2026 |  | Cast a Wider Net: Coordinated Pass@K Policy Optimization for Code Reasoning ([link](https://www.semanticscholar.org/paper/24ed88680bbf7256746a6e6995ff9a86817b56fe)) | Yilong Li, Suman Banerjee, and Tong Che |  |
| 35 | 2026 |  | Beyond pass@k: Redundancy-Aware RLVR for Multi-Sample Code Generation ([link](https://www.semanticscholar.org/paper/a16b15ae619e0ba0560027e7746aa3ae03af5157)) | Lecadre Florian, Alexandre Verine, Rio Yokota, and Benjamin Négrevergne |  |
| 36 | 2026 | 9.6 | Reinforced Efficient Reasoning via Semantically Diverse Exploration ([link](https://doi.org/10.48550/arXiv.2601.05053)) | Ziqi Zhao et al. | ArXiv |
| 37 | 2026 | 6.0 | Learning to Explore with Parameter-Space Noise: A Deep Dive into Parameter-Space Noise for Reinforcement Learning with Verifiable Rewards ([link](https://doi.org/10.48550/arXiv.2602.02555)) | Bizhe Bai, Xinyue Wang, Peng Ye, and Tao Chen | ArXiv |
| 38 | 2026 |  | Deep Dense Exploration for LLM Reinforcement Learning via Pivot-Driven Resampling ([link](https://doi.org/10.48550/arXiv.2602.14169)) | Yiran Guo et al. | ArXiv |
| 39 | 2025 | 11 | Lookahead Tree-Based Rollouts for Enhanced Trajectory-Level Exploration in Reinforcement Learning with Verifiable Rewards ([link](https://doi.org/10.48550/arXiv.2510.24302)) | Shangyu Xing, Siyuan Wang, Chenyuan Yang, Xinyu Dai, and Xiang Ren | ArXiv |
| 40 | 2026 | 2.0 | How You Begin is How You Reason: Driving Exploration in RLVR via Prefix-Tuned Priors ([link](https://www.semanticscholar.org/paper/78f8f1358752e26cac98016e1ee2c4a75cf3fb39)) | Yifan Xu, Junren Chen, and Yifan Chen |  |
| 41 | 2026 | 14 | DSDR: Dual-Scale Diversity Regularization for Exploration in LLM Reasoning ([link](https://doi.org/10.48550/arXiv.2602.19895)) | Zhongwei Wan et al. | ArXiv |
| 42 | 2026 | 4.0 | Leveraging Error Diversity in Group Rollouts for Reinforcement Learning ([link](https://www.semanticscholar.org/paper/0398c4b3f10abfff1db33948ff8f16be1c119d98)) | Wenpu Liu et al. |  |
| 43 | 2025 | 16 | Can LLMs Guide Their Own Exploration? Gradient-Guided Reinforcement Learning for LLM Reasoning ([link](https://doi.org/10.48550/arXiv.2512.15687)) | Zhenwen Liang et al. | ArXiv |
| 44 | 2025 | 55 | Rethinking Entropy Interventions in RLVR: An Entropy Change Perspective ([link](https://doi.org/10.48550/arXiv.2510.10150)) | Zhezheng Hao et al. | ArXiv |
| 45 | 2025 | 19 | XRPO: Pushing the limits of GRPO with Targeted Exploration and Exploitation ([link](https://doi.org/10.48550/arXiv.2510.06672)) | Udbhav Bamba, Minghao Fang, Yifan Yu, Haizhong Zheng, and Fan Lai | ArXiv |
| 46 | 2025 | 9.2 | Revisiting Entropy Regularization: Adaptive Coefficient Unlocks Its Potential for LLM Reinforcement Learning ([link](https://doi.org/10.18653/v1/2026.findings-acl.895)) | Xiaoyun Zhang et al. | Findings of the Association for Computational Linguistics: ACL 2026 |
| 47 | 2025 | 341 | The Entropy Mechanism of Reinforcement Learning for Reasoning Language Models ([link](https://doi.org/10.48550/arXiv.2505.22617)) | Ganqu Cui et al. | ArXiv |
| 48 | 2025 | 2.8 | Do Not Step Into the Same River Twice: Learning to Reason from Trial and Error ([link](https://doi.org/10.48550/arXiv.2510.26109)) | Chenming Tang, Hsiu-Yuan Huang, Weijie Liu, Saiyong Yang, and Yunfang Wu | ArXiv |
| 49 | 2025 | 451 | Beyond the 80/20 Rule: High-Entropy Minority Tokens Drive Effective Reinforcement Learning for LLM Reasoning ([link](https://doi.org/10.48550/arXiv.2506.01939)) | Shenzhi Wang et al. | ArXiv |
| 50 | 2026 | 12 | F-GRPO: Don’t Let Your Policy Learn the Obvious and Forget the Rare ([link](https://doi.org/10.48550/arXiv.2602.06717)) | Daniil Plyusov et al. | ArXiv |
| 51 | 2025 | 38 | First Return, Entropy-Eliciting Explore ([link](https://doi.org/10.48550/arXiv.2507.07017)) | Tianyu Zheng et al. | ArXiv |
| 52 | 2025 |  | The Road Less Traveled: Enhancing Exploration in LLMs via Sequential Sampling ([link](https://doi.org/10.48550/arXiv.2510.15502)) | Shijia Kang and Muhan Zhang | ArXiv |
| 53 | 2025 | 39 | Depth-Breadth Synergy in RLVR: Unlocking LLM Reasoning Gains with Adaptive Exploration ([link](https://doi.org/10.48550/arXiv.2508.13755)) | Zhicheng YANG et al. | ArXiv |
| 54 | 2026 | 2.0 | Transformation-Augmented GRPO for Enhancing Exploration in Reasoning of Large Language Models ([link](https://www.semanticscholar.org/paper/3d2778fc969edf37ff3ba3c40c523d7d114242e4)) | Khiem Le et al. |  |
| 55 | 2025 | 10 | Explore Data Left Behind in Reinforcement Learning for Reasoning Language Models ([link](https://doi.org/10.48550/arXiv.2511.04800)) | Chenxi Liu et al. | ArXiv |
| 56 | 2024 | 136 | Rewarding Progress: Scaling Automated Process Verifiers for LLM Reasoning ([link](https://doi.org/10.48550/arXiv.2410.08146)) | Amrith Rajagopal Setlur et al. | ArXiv |
| 57 | 2026 | 58 | Look Inward to Explore Outward: Learning Temperature Policy from LLM Internal States via Hierarchical RL ([link](https://doi.org/10.48550/arXiv.2602.13035)) | Yixiao Zhou, Yang Li, Dongzhou Cheng, Hehe Fan, and Yu Cheng | ArXiv |
| 58 | 2022 | 26 | Language Models Can Teach Themselves to Program Better ([link](https://doi.org/10.48550/arXiv.2207.14502)) | Patrick M. Haluptzok, Matthew Bowers, and A. Kalai | ArXiv |
| 59 |  | 6 | Codeplay: Autotelic Learning through Collaborative Self-Play in Programming Environments ([link](https://www.semanticscholar.org/paper/e5f797f502349ec3241cef5de3b05e2f7e09ba82)) | Laetitia Teodorescu, Matthew Bowers, and P. Oudeyer |  |
| 60 | 2025 | 35 | Self-Questioning Language Models ([link](https://doi.org/10.48550/arXiv.2508.03682)) | Lili Chen, Mihir Prabhudesai, Katerina Fragkiadaki, Hao Liu, and Deepak Pathak | ArXiv |
| 61 | 2025 | 42 | Toward Training Superintelligent Software Agents through Self-Play SWE-RL ([link](https://doi.org/10.48550/arXiv.2512.18552)) | Yuxiang Wei et al. | ArXiv |
| 62 | 2026 | 6.0 | Reaching Beyond the Mode: RL for Distributional Reasoning in Language Models ([link](https://doi.org/10.48550/arXiv.2603.24844)) | Isha Puri et al. | ArXiv |
| 63 | 2026 |  | ZeroCoder: Can LLMs Improve Code Generation Without Ground-Truth Supervision? ([link](https://doi.org/10.48550/arXiv.2604.07864)) | Lishui Fan et al. | ArXiv |
| 64 | 2026 | 2.0 | Think Longer to Explore Deeper: Learn to Explore In-Context via Length-Incentivized Reinforcement Learning ([link](https://doi.org/10.48550/arXiv.2602.11748)) | Futing Wang et al. | ArXiv |
| 65 |  | 3 | Quality-Diversity Self-Play: Open-Ended Strategy Innovation via Foundation Models ([link](https://www.semanticscholar.org/paper/9ddb806c60c9e43858bdecddeab41fbc97878113)) | Aaron Dharna, Cong Lu, and Jeff Clune |  |
| 66 | 2025 | 124 | ShinkaEvolve: Towards Open-Ended And Sample-Efficient Program Evolution ([link](https://doi.org/10.48550/arXiv.2509.19349)) | R. Lange, Yuki Imajuku, and Edoardo Cetin | ArXiv |
| 67 | 2023 | 406 | Mathematical discoveries from program search with large language models ([link](https://doi.org/10.1038/s41586-023-06924-6)) | B. Romera-Paredes et al. | Nature |
| 68 | 2026 | 2.0 | LLM-Based Scientific Equation Discovery via Physics-Informed Token-Regularized Policy Optimization ([link](https://doi.org/10.48550/arXiv.2602.10576)) | Boxiao Wang et al. | ArXiv |
| 69 | 2026 |  | Game-Theoretic Co-Evolution for LLM-Based Heuristic Discovery ([link](https://doi.org/10.48550/arXiv.2601.22896)) | Xinyi Ke, Kai Li, Junliang Xing, Yifan Zhang, and Jian Cheng | ArXiv |
| 70 | 2022 | 37 | Evolution through Large Models ([link](https://www.semanticscholar.org/paper/4baac6b8fa7731352004bc45d2ba2b6bbd04a4e7)) | J. Lehman et al. |  |
| 71 | 2023 | 2.0 | ACES: Generating Diverse Programming Puzzles with Autotelic Language Models and Semantic Descriptors ([link](https://doi.org/10.48550/arXiv.2310.10692)) | Julien Pourcel, Cédric Colas, P. Oudeyer, and Laetitia Teodorescu | ArXiv |
| 72 | 2026 |  | Improving HPC Code Generation Capability of LLMs via Online Reinforcement Learning with Real-Machine Benchmark Rewards ([link](https://doi.org/10.48550/arXiv.2602.12049)) | Ryo Mikasa, Shun-ichiro Hayashi, Daichi Mukunoki, Tetsuya Hoshino, and Takahiro Katagiri | ArXiv |

### Paper Details

1\. · 100% match · 2025 · 17 cit/yr\
**Representation-Based Exploration for Language Models: From Test-Time to Post-Training** ([link](https://doi.org/10.48550/arXiv.2510.11686))\
Jens Tuyls, Dylan J. Foster, Akshay Krishnamurthy, and Jordan T. Ash\
*ArXiv* · Oct 13, 2025 · 13 citations

> Reinforcement learning (RL) promises to expand the capabilities of language models, but it is unclear if current RL techniques promote the discovery of novel behaviors, or simply sharpen those already present in the base model. In this paper, we investigate the value of deliberate exploration – explicitly incentivizing the model to discover novel and diverse behaviors – and aim to understand how the knowledge in pre-trained models can guide this search. Our main finding is that exploration with a simple, principled, representation-based bonus derived from the pre-trained language model’s hidden states significantly improves diversity and pass@k rates – both for post-training, and in a novel inference-time scaling setting we introduce. For inference-time, exploration with representation-based diversity improves efficiency, consistently improving pass@k rates across a variety of models and reasoning tasks. For example, for Qwen-2.5-14b-Instruct we obtain over 50% improvement in verifier efficiency on almost all tasks. For post-training, we show that integrating this exploration strategy into an RL pipeline improves reasoning performance over that of the initial model and over standard RL post-training. For example, on AIME 2024, our post-trained Qwen-2.5-7b-Instruct’s pass@80 matches the pass@256 of GRPO on the same model, demonstrating a 3x improvement in test-time sample efficiency. Overall, our findings suggest that deliberate exploration – with the right notion of diversity – is a practical path toward discovery of new behaviors beyond sharpening.

------------------------------------------------------------------------

2\. · 100% match · 2025 · 88 cit/yr\
**Outcome-based Exploration for LLM Reasoning** ([link](https://doi.org/10.48550/arXiv.2509.06941))\
Yuda Song, Julia Kempe, and Rémi Munos\
*ArXiv* · Sep 8, 2025 · 75 citations

> Reinforcement learning (RL) has emerged as a powerful method for improving the reasoning abilities of large language models (LLMs). Outcome-based RL, which rewards policies solely for the correctness of the final answer, yields substantial accuracy gains but also induces a systematic loss in generation diversity. This collapse undermines real-world performance, where diversity is critical for test-time scaling. We analyze this phenomenon by viewing RL post-training as a sampling process and show that, strikingly, RL can reduce effective diversity even on the training set relative to the base model. Our study highlights two central findings: (i) a transfer of diversity degradation, where reduced diversity on solved problems propagates to unsolved ones, and (ii) the tractability of the outcome space, since reasoning tasks admit only a limited set of distinct answers. Motivated by these insights, we propose outcome-based exploration, which assigns exploration bonuses according to final outcomes. We introduce two complementary algorithms: historical exploration, which encourages rarely observed answers via UCB-style bonuses, and batch exploration, which penalizes within-batch repetition to promote test-time diversity. Experiments on standard competition math with Llama and Qwen models demonstrate that both methods improve accuracy while mitigating diversity collapse. On the theoretical side, we formalize the benefit of outcome-based exploration through a new model of outcome-based bandits. Together, these contributions chart a practical path toward RL methods that enhance reasoning without sacrificing the diversity essential for scalable deployment.

------------------------------------------------------------------------

3\. · 100% match · 2025 · 67 cit/yr\
**Rewarding the Unlikely: Lifting GRPO Beyond Distribution Sharpening** ([link](https://doi.org/10.48550/arXiv.2506.02355))\
Andre He, Daniel Fried, and S. Welleck\
*Conference on Empirical Methods in Natural Language Processing* · Jun 3, 2025 · 75 citations

> Reinforcement learning is emerging as a primary driver for improving language model reasoning capabilities. A fundamental question is whether current reinforcement learning algorithms – such as Group Relative Policy Optimization (GRPO), the de facto standard algorithm used to improve language model reasoning – merely sharpen the base model’s distribution around problems it can already solve. We investigate this question in the context of formal theorem proving, which has access to a perfect verifier. We identify a degenerate rank bias in GRPO in which highly probable trajectories are reinforced and rare ones are neglected. This results in distribution sharpening: the model can solve some problems with fewer samples, but underperforms simply sampling more solutions from the original model. To overcome GRPO’s rank bias we introduce unlikeliness reward, a simple method for explicitly up-weighting rare but correct solutions. We show that unlikeliness reward mitigates rank bias and improves pass@$`N`$ across a large range of $`N`$ in both synthetic and real theorem proving settings. We also uncover an unexpected link between rank bias and a seemingly mundane hyperparameter – the number of updates per batch – that leads to a second, complementary mitigation. We combine our insights into a revised GRPO training recipe for formal theorem proving, yielding an open pipeline that achieves competitive performance to DeepSeek-Prover-V1.5-RL on the miniF2F-test benchmark. We release our implementation at https://github.com/AndreHe02/rewarding-unlikely-release

------------------------------------------------------------------------

4\. · 100% match · 2024 · 11 cit/yr\
**Formal Theorem Proving by Rewarding LLMs to Decompose Proofs Hierarchically** ([link](https://doi.org/10.48550/arXiv.2411.01829))\
Kefan Dong, Arvind V. Mahankali, and Tengyu Ma\
*ArXiv* · Nov 4, 2024 · 19 citations

> Mathematical theorem proving is an important testbed for large language models’ deep and abstract reasoning capability. This paper focuses on improving LLMs’ ability to write proofs in formal languages that permit automated proof verification/evaluation. Most previous results provide human-written lemmas to the theorem prover, which is an arguably oversimplified setting that does not sufficiently test the provers’ planning and decomposition capabilities. Instead, we work in a more natural setup where the lemmas that are directly relevant to the theorem are not given to the theorem prover at test time. We design an RL-based training algorithm that encourages the model to decompose a theorem into lemmas, prove the lemmas, and then prove the theorem by using the lemmas. Our reward mechanism is inspired by how mathematicians train themselves: even if a theorem is too challenging to be proved by the current model, a positive reward is still given to the model for any correct and novel lemmas that are proposed and proved in this process. During training, our model proposes and proves lemmas that are not in the training dataset. In fact, these newly-proposed correct lemmas consist of 37.7% of the training replay buffer when we train on the dataset extracted from Archive of Formal Proofs (AFP). The model trained by our RL algorithm outperforms that trained by supervised finetuning, improving the pass rate from 40.8% to 45.5% on AFP test set, and from 36.5% to 39.5% on an out-of-distribution test set.

------------------------------------------------------------------------

5\. · 100% match · 2025 · 224 cit/yr\
**Absolute Zero: Reinforced Self-play Reasoning with Zero Data** ([link](https://doi.org/10.48550/arXiv.2505.03335))\
Andrew Zhao et al.\
*ArXiv* · May 6, 2025 · 268 citations

> Reinforcement learning with verifiable rewards (RLVR) has shown promise in enhancing the reasoning capabilities of large language models by learning directly from outcome-based rewards. Recent RLVR works that operate under the zero setting avoid supervision in labeling the reasoning process, but still depend on manually curated collections of questions and answers for training. The scarcity of high-quality, human-produced examples raises concerns about the long-term scalability of relying on human supervision, a challenge already evident in the domain of language model pretraining. Furthermore, in a hypothetical future where AI surpasses human intelligence, tasks provided by humans may offer limited learning potential for a superintelligent system. To address these concerns, we propose a new RLVR paradigm called Absolute Zero, in which a single model learns to propose tasks that maximize its own learning progress and improves reasoning by solving them, without relying on any external data. Under this paradigm, we introduce the Absolute Zero Reasoner (AZR), a system that self-evolves its training curriculum and reasoning ability by using a code executor to both validate proposed code reasoning tasks and verify answers, serving as an unified source of verifiable reward to guide open-ended yet grounded learning. Despite being trained entirely without external data, AZR achieves overall SOTA performance on coding and mathematical reasoning tasks, outperforming existing zero-setting models that rely on tens of thousands of in-domain human-curated examples. Furthermore, we demonstrate that AZR can be effectively applied across different model scales and is compatible with various model classes.

------------------------------------------------------------------------

6\. · 100% match · 2025 · 50 cit/yr\
**STP: Self-play LLM Theorem Provers with Iterative Conjecturing and Proving** ([link](https://doi.org/10.48550/arXiv.2502.00212))\
Kefan Dong and Tengyu Ma\
*ArXiv* · Jan 31, 2025 · 73 citations

> A fundamental challenge in formal theorem proving by LLMs is the lack of high-quality training data. Although reinforcement learning or expert iteration partially mitigates this issue by alternating between LLM generating proofs and finetuning them on correctly generated ones, performance quickly plateaus due to the scarcity of correct proofs (sparse rewards). To keep improving the models with limited data, we draw inspiration from mathematicians, who continuously develop new results, partly by proposing novel conjectures or exercises (which are often variants of known results) and attempting to solve them. We design the Self-play Theorem Prover (STP) that simultaneously takes on two roles, conjecturer and prover, each providing training signals to the other. The conjecturer is trained iteratively on previously generated conjectures that are barely provable by the current prover, which incentivizes it to generate increasingly challenging conjectures over time. The prover attempts to prove the conjectures with standard expert iteration. We evaluate STP with both Lean and Isabelle formal versifiers. With 51.3 billion tokens generated during the training in Lean, STP proves 28.5% of the statements in the LeanWorkbook dataset, doubling the previous best result of 13.2% achieved through expert iteration. The final model achieves state-of-the-art performance among whole-proof generation methods on miniF2F-test (65.0%, pass@3200), Proofnet-test (23.9%, pass@3200) and PutnamBench (8/644, pass@3200). We release our code, model, and dataset in this URL: https://github.com/kfdong/STP.

------------------------------------------------------------------------

7\. · 100% match · 2025 · 75 cit/yr\
**Jointly Reinforcing Diversity and Quality in Language Model Generations** ([link](https://doi.org/10.48550/arXiv.2509.02534))\
Tianjian Li et al.\
*ArXiv* · Sep 2, 2025 · 65 citations

> Post-training of Large Language Models (LMs) often prioritizes accuracy and helpfulness at the expense of diversity. This creates a tension: while post-training improves response quality, it also sharpens output distributions and reduces the range of ideas, limiting the usefulness of LMs in creative and exploratory tasks such as brainstorming, storytelling, or problem solving. We address this challenge with Diversity-Aware Reinforcement Learning (DARLING), a framework that jointly optimizes for response quality and semantic diversity. At its core, DARLING introduces a learned partition function to measure diversity beyond surface-level lexical variations. This diversity signal is then combined with a quality reward during online reinforcement learning, encouraging models to generate outputs that are both high-quality and distinct. Experiments across multiple model families and sizes show that DARLING generalizes to two regimes: non-verifiable tasks (instruction following and creative writing) and verifiable tasks (competition math). On five benchmarks in the first setting, DARLING consistently outperforms quality-only RL baselines, producing outputs that are simultaneously of higher quality and novelty. In the second setting, DARLING achieves higher pass@1 (solution quality) and pass@k (solution variety). Most strikingly, explicitly optimizing for diversity catalyzes exploration in online RL, which manifests itself as higher-quality responses.

------------------------------------------------------------------------

8\. · 100% match · 2025 · 34 cit/yr\
**Diversity-Aware Policy Optimization for Large Language Model Reasoning** ([link](https://doi.org/10.48550/arXiv.2505.23433))\
Jian Yao, Ran Cheng, Xingyu Wu, Jibin Wu, and Kay Chen Tan\
*ArXiv* · May 29, 2025 · 39 citations

> The reasoning capabilities of large language models (LLMs) have advanced rapidly, particularly following the release of DeepSeek R1, which has inspired a surge of research into data quality and reinforcement learning (RL) algorithms. Despite the pivotal role diversity plays in RL, its influence on LLM reasoning remains largely underexplored. To bridge this gap, this work presents a systematic investigation into the impact of diversity in RL-based training for LLM reasoning, and proposes a novel diversity-aware policy optimization method. Across evaluations on 12 LLMs, we observe a strong positive correlation between the solution diversity and Potential at k (a novel metric quantifying an LLM’s reasoning potential) in high-performing models. This finding motivates our method to explicitly promote diversity during RL training. Specifically, we design a token-level diversity and reformulate it into a practical objective, then we selectively apply it to positive samples. Integrated into the R1-zero training framework, our method achieves a 3.5 percent average improvement across four mathematical reasoning benchmarks, while generating more diverse and robust solutions.

------------------------------------------------------------------------

9\. · 100% match · 2026 · 4.0 cit/yr\
**SetPO: Set-Level Policy Optimization for Diversity-Preserving LLM Reasoning** ([link](https://doi.org/10.48550/arXiv.2602.01062))\
Chenyi Li et al.\
*ArXiv* · Feb 1, 2026 · 2 citations

> Reinforcement learning with verifiable rewards has shown notable effectiveness in enhancing large language models (LLMs) reasoning performance, especially in mathematics tasks. However, such improvements often come with reduced outcome diversity, where the model concentrates probability mass on a narrow set of solutions. Motivated by diminishing-returns principles, we introduce a set level diversity objective defined over sampled trajectories using kernelized similarity. Our approach derives a leave-one-out marginal contribution for each sampled trajectory and integrates this objective as a plug-in advantage shaping term for policy optimization. We further investigate the contribution of a single trajectory to language model diversity within a distribution perturbation framework. This analysis theoretically confirms a monotonicity property, proving that rarer trajectories yield consistently higher marginal contributions to the global diversity. Extensive experiments across a range of model scales demonstrate the effectiveness of our proposed algorithm, consistently outperforming strong baselines in both Pass@1 and Pass@K across various benchmarks.

------------------------------------------------------------------------

10\. · 100% match · 2025 · 55 cit/yr\
**Pass@K Policy Optimization: Solving Harder Reinforcement Learning Problems** ([link](https://doi.org/10.48550/arXiv.2505.15201))\
Christian J. Walder and Deep Karkhanis\
*ArXiv* · May 21, 2025 · 63 citations

> Reinforcement Learning (RL) algorithms sample multiple n\>1 solution attempts for each problem and reward them independently. This optimizes for pass@1 performance and prioritizes the strength of isolated samples at the expense of the diversity and collective utility of sets of samples. This under-utilizes the sampling capacity, limiting exploration and eventual improvement on harder examples. As a fix, we propose Pass-at-k Policy Optimization (PKPO), a transformation on the final rewards which leads to direct optimization of pass@k performance, thus optimizing for sets of samples that maximize reward when considered jointly. Our contribution is to derive novel low variance unbiased estimators for pass@k and its gradient, in both the binary and continuous reward settings. We show optimization with our estimators reduces to standard RL with rewards that have been jointly transformed by a stable and efficient transformation function. While previous efforts are restricted to k=n, ours is the first to enable robust optimization of pass@k for any arbitrary k\<= n. Moreover, instead of trading off pass@1 performance for pass@k gains, our method allows annealing k during training, optimizing both metrics and often achieving strong pass@1 numbers alongside significant pass@k gains. We validate our reward transformations on toy experiments, which reveal the variance reducing properties of our formulations. We also include real-world examples using the open-source LLM, GEMMA-2. We find that our transformation effectively optimizes for the target k. Furthermore, higher k values enable solving more and harder problems, while annealing k boosts both the pass@1 and pass@k . Crucially, for challenging task sets where conventional pass@1 optimization stalls, our pass@k approach unblocks learning, likely due to better exploration by prioritizing joint utility over the utility of individual samples.

------------------------------------------------------------------------

11\. · 100% match · 2025 · 26 cit/yr\
**Diversity-Incentivized Exploration for Versatile Reasoning** ([link](https://doi.org/10.48550/arXiv.2509.26209))\
Zican Hu et al.\
*ArXiv* · Sep 30, 2025 · 21 citations

> Reinforcement Learning with Verifiable Rewards (RLVR) has emerged as a crucial paradigm for incentivizing reasoning capabilities in Large Language Models (LLMs). Due to vast state-action spaces and reward sparsity in reasoning tasks, existing methods often struggle with deficient exploration and poor sample efficiency. In the paper, we propose \textbf{DIVER} (\textbf{D}iversity-\textbf{I}ncentivized Exploration for \textbf{V}ersatil\textbf{E} \textbf{R}easoning), an innovative framework that highlights the pivotal role of global sequence-level diversity to incentivize deep exploration for versatile reasoning. We first conduct a primary empirical study to reveal a strong positive correlation between global diversity and reasoning capacity. Building on this insight, we introduce global diversity incentives as an intrinsic reward to promote deep exploration in a semantically structured space. Incorporating the intrinsic reward, we develop a potential-based reward shaping mechanism to preserve optimal policy invariance and design simple heuristics to mitigate possible reward hacking. Experimental results show that DIVER outperforms competitive RLVR baselines with various exploration strategies on both in-domain and out-of-domain tasks, excelling in both Pass@1 and Pass@k evaluations. Our code is available at https://github.com/NJU-RL/DIVER.

------------------------------------------------------------------------

12\. · 100% match · 2025 · 129 cit/yr\
**Pass@k Training for Adaptively Balancing Exploration and Exploitation of Large Reasoning Models** ([link](https://doi.org/10.48550/arXiv.2508.10751))\
Zhipeng Chen et al.\
*ArXiv* · Aug 14, 2025 · 119 citations

> Reinforcement learning with verifiable rewards (RLVR), which typically adopts Pass@1 as the reward, has faced the issues in balancing exploration and exploitation, causing policies to prefer conservative actions, converging to a local optimum. Identifying an appropriate reward metric is therefore crucial. Regarding the prior work, although Pass@k has been used in evaluation, its connection to LLM exploration ability in RLVR remains largely overlooked. To investigate this, we first use Pass@k as the reward to train the policy model (i.e., $`\textbf{Pass@k Training}`$), and observe the improvement on its exploration ability. Next, we derive an analytical solution for the advantage of Pass@k Training, leading to an efficient and effective process. Building on this, our analysis reveals that exploration and exploitation are not inherently conflicting objectives, while they can mutually enhance each other. Moreover, Pass@k Training with analytical derivation essentially involves directly designing the advantage function. Inspired by this, we preliminarily explore the advantage design for RLVR, showing promising results and highlighting a potential future direction.

------------------------------------------------------------------------

13\. · 100% match · 2026\
**ExTra: Exploratory Trajectory Optimization for Language Model Reinforcement Learning** ([link](https://www.semanticscholar.org/paper/ba42dbb6e6ac459e0f1ffbdfe0b1e3b65c3eb638))\
Wenyang Hu et al.\
Jun 23, 2026 · 0 citations

> Reinforcement Learning with Verifiable Rewards (RLVR) for language-model reasoning can fail at both extremes of task difficulty: easy prompts often produce all-correct, low-diversity rollout groups with little gradient signal, while hard prompts can produce all-incorrect groups with no positive reward. We introduce ExTra (Exploratory Trajectory Optimization), a GRPO-compatible framework that extracts exploration signals from the model’s own rollouts. ExTra combines two mechanisms: (i) a novelty reward that adds embedding-based diversity bonuses after GRPO normalization, rewarding diverse correct solutions; and (ii) entropy-guided prefix regeneration, which scores partial trajectories using entropy signals and continues exploration from promising intermediate steps. Across six mathematical reasoning benchmarks, ExTra improves Qwen3-1.7B over GRPO by about +5 points on pass@1 and +7 points on pass@16, showing that trajectory-level exploration signals can improve both single-sample accuracy and inference-time coverage.

------------------------------------------------------------------------

14\. · 100% match · 2026 · 14 cit/yr\
**Rewarding the Rare: Uniqueness-Aware RL for Creative Problem Solving in LLMs** ([link](https://doi.org/10.48550/arXiv.2601.08763))\
Zhiyuan Hu et al.\
*ArXiv* · Jan 13, 2026 · 7 citations

> Reinforcement learning (RL) has become a central paradigm for post-training large language models (LLMs), particularly for complex reasoning tasks, yet it often suffers from exploration collapse: policies prematurely concentrate on a small set of dominant reasoning patterns, improving pass@1 while limiting rollout-level diversity and gains in pass@k. We argue that this failure stems from regularizing local token behavior rather than diversity over sets of solutions. To address this, we propose Uniqueness-Aware Reinforcement Learning, a rollout-level objective that explicitly rewards correct solutions that exhibit rare high-level strategies. Our method uses an LLM-based judge to cluster rollouts for the same problem according to their high-level solution strategies, ignoring superficial variations, and reweights policy advantages inversely with cluster size. As a result, correct but novel strategies receive higher rewards than redundant ones. Across mathematics, physics, and medical reasoning benchmarks, our approach consistently improves pass@$`k`$ across large sampling budgets and increases the area under the pass@$`k`$ curve (AUC@$`K`$) without sacrificing pass@1, while sustaining exploration and uncovering more diverse solution strategies at scale.

------------------------------------------------------------------------

15\. · 100% match · 2025 · 53 cit/yr\
**Evolving Language Models without Labels: Majority Drives Selection, Novelty Promotes Variation** ([link](https://doi.org/10.48550/arXiv.2509.15194))\
Yujun Zhou et al.\
*ArXiv* · Sep 18, 2025 · 44 citations

> Large language models (LLMs) are increasingly trained with reinforcement learning from verifiable rewards (RLVR), yet real-world deployment demands models that can self-improve without labels or external judges. Existing self-improvement approaches primarily rely on self-confirmation signals (e.g., confidence, entropy, or consistency) to generate rewards. This reliance drives models toward over-confident, majority-favored solutions, causing an entropy collapse that degrades pass@n and reasoning complexity. To address this, we propose EVOL-RL, a label-free framework that mirrors the evolutionary principle of balancing selection with variation. Concretely, EVOL-RL retains the majority-voted answer as an anchor for stability, but adds a novelty-aware reward that scores each sampled solution by how different its reasoning is from other concurrently generated responses. This majority-for-stability + novelty-for-exploration rule mirrors the variation-selection principle: selection prevents drift, while novelty prevents collapse. Evaluation results show that EVOL-RL consistently outperforms the majority-only baseline; e.g., training on label-free AIME24 lifts Qwen3-4B-Base AIME25 pass@1 from baseline’s 4.6% to 16.4%, and pass@16 from 18.5% to 37.9%. EVOL-RL not only prevents in-domain diversity collapse but also improves out-of-domain generalization (from math reasoning to broader tasks, e.g., MMLU-Pro and BBEH). The code is available at: https://github.com/YujunZhou/EVOL-RL.

------------------------------------------------------------------------

16\. · 100% match · 2025 · 16 cit/yr\
**Beyond the Sampled Token: Preserving Candidate Support in RLVR** ([link](https://www.semanticscholar.org/paper/4af03e3796c0767104581ca8d56f01824d3e9e52))\
Ruotian Peng, Yi Ren, Zhouliang Yu, Weiyang Liu, and Yandong Wen\
Oct 16, 2025 · 12 citations

> We revisit exploration collapse in reinforcement learning with verifiable rewards (RLVR), from the perspective of the \emph{candidate distribution} for next-token prediction. We formally show that as probability concentrates on the top-$`1`$ candidate, the expected number of distinct responses collapses to one regardless of the sampling budget $`K`$. This theoretical implication is further verified by our empirical tracking of top-$`N`$ candidate probabilities during training, where the top-$`1`$ candidate progressively dominates while plausible alternatives are suppressed. These findings suggest a key desideratum for effective exploration: \emph{preserving non-negligible probability mass on the top-$`N`$ candidates}. To this end, we propose Candidate-aware Support Preservation (CaSP), with two complementary designs. Specifically, CaSP redistributes positive gradients among top-$`N`$ candidates for correct responses, and applies a stronger penalty to the top-$`1`$ candidate for incorrect responses. Unlike many exploration-oriented methods that improve pass@$`K`$ at the cost of pass@1, CaSP improves pass@$`K`$ across the full $`K`$ spectrum. These gains generalize to 6 math, 2 logical-reasoning, and 2 coding benchmarks, and scales to 32B-parameter models and sampling budgets up to $`K=1024`$, positioning it as a principled, candidate-level approach for RLVR exploration.

------------------------------------------------------------------------

17\. · 100% match · 2025 · 36 cit/yr\
**The Choice of Divergence: A Neglected Key to Mitigating Diversity Collapse in Reinforcement Learning with Verifiable Reward** ([link](https://doi.org/10.48550/arXiv.2509.07430))\
Long Li et al.\
*ArXiv* · Sep 9, 2025 · 31 citations

> A central paradox in fine-tuning Large Language Models (LLMs) with Reinforcement Learning with Verifiable Reward (RLVR) is the frequent degradation of multi-attempt performance (Pass@k) despite improvements in single-attempt accuracy (Pass@1). This is often accompanied by catastrophic forgetting, where models lose previously acquired skills. While various methods have been proposed, the choice and function of the divergence term have been surprisingly unexamined as a proactive solution. We argue that standard RLVR objectives – both those using the mode-seeking reverse KL-divergence and those forgoing a divergence term entirely – lack a crucial mechanism for knowledge retention. The reverse-KL actively accelerates this decay by narrowing the policy, while its absence provides no safeguard against the model drifting from its diverse knowledge base. We propose a fundamental shift in perspective: using the divergence term itself as the solution. Our framework, Diversity-Preserving Hybrid RL (DPH-RL), leverages mass-covering f-divergences (like forward-KL and JS-divergence) to function as a rehearsal mechanism. By continuously referencing the initial policy, this approach forces the model to maintain broad solution coverage. Extensive experiments on math and SQL generation demonstrate that DPH-RL not only resolves the Pass@k degradation but improves both Pass@1 and Pass@k in- and out-of-domain. Additionally, DPH-RL is more training-efficient because it computes f-divergence using generator functions, requiring only sampling from the initial policy and no online reference model. Our work highlights a crucial, overlooked axis for improving RLVR, demonstrating that the proper selection of a divergence measure is a powerful tool for building more general and diverse reasoning models.

------------------------------------------------------------------------

18\. · 100% match · 2025 · 253 cit/yr\
**Reasoning with Exploration: An Entropy Perspective** ([link](https://doi.org/10.48550/arXiv.2506.14758))\
Daixuan Cheng et al.\
*AAAI Conference on Artificial Intelligence* · Jun 17, 2025 · 274 citations

> Balancing exploration and exploitation is a central goal in reinforcement learning (RL). Despite recent advances in enhancing language model (LM) reasoning, most methods lean toward exploitation, and increasingly encounter performance plateaus. In this work, we revisit entropy – a signal of exploration in RL – and examine its relationship to exploratory reasoning in LMs. Through empirical analysis, we uncover positive correlations between high-entropy regions and three types of exploratory reasoning actions: (1) pivotal tokens that determine or connect logical steps, (2) reflective actions such as self-verification and correction, and (3) rare behaviors under-explored by the base LMs. Motivated by this, we introduce a minimal modification to standard RL with only one line of code: augmenting the advantage function with an entropy-based term. Unlike traditional maximum-entropy methods which encourage exploration by promoting uncertainty, we encourage exploration by promoting deeper and longer reasoning chains. Notably, our method achieves significant gains on the Pass@K metric – an upper-bound estimator of LM reasoning capabilities – even when evaluated with extremely large K values, pushing the boundaries of LM reasoning.

------------------------------------------------------------------------

19\. · 100% match · 2024 · 23 cit/yr\
**Learning Formal Mathematics From Intrinsic Motivation** ([link](https://doi.org/10.48550/arXiv.2407.00695))\
Gabriel Poesia, David Broman, Nick Haber, and Noah D. Goodman\
*ArXiv* · Jun 30, 2024 · 47 citations

> How did humanity coax mathematics from the aether? We explore the Platonic view that mathematics can be discovered from its axioms - a game of conjecture and proof. We describe Minimo (Mathematics from Intrinsic Motivation): an agent that jointly learns to pose challenging problems for itself (conjecturing) and solve them (theorem proving). Given a mathematical domain axiomatized in dependent type theory, we first combine methods for constrained decoding and type-directed synthesis to sample valid conjectures from a language model. Our method guarantees well-formed conjectures by construction, even as we start with a randomly initialized model. We use the same model to represent a policy and value function for guiding proof search. Our agent targets generating hard but provable conjectures - a moving target, since its own theorem proving ability also improves as it trains. We propose novel methods for hindsight relabeling on proof search trees to significantly improve the agent’s sample efficiency in both tasks. Experiments on 3 axiomatic domains (propositional logic, arithmetic and group theory) demonstrate that our agent can bootstrap from only the axioms, self-improving in generating true and challenging conjectures and in finding proofs.

------------------------------------------------------------------------

20\. · 99% match · 2025 · 7.0 cit/yr\
**Propose, Solve, Verify: Self-Play Through Formal Verification** ([link](https://doi.org/10.48550/arXiv.2512.18160))\
Alex Wilf et al.\
*ArXiv* · Dec 20, 2025 · 4 citations

> Training models through self-play alone (without any human data) has been a longstanding goal in AI, but its effectiveness for training large language models remains unclear, particularly in code generation where rewards based on unit tests are brittle and prone to error propagation. We study self-play in the verified code generation setting, where formal verification provides reliable correctness signals. We introduce Propose, Solve, Verify (PSV) a simple self-play framework where formal verification signals are used to create a proposer capable of generating challenging synthetic problems and a solver trained via expert iteration. We use PSV to train PSV-Verus, which across three benchmarks improves pass@1 by up to 9.6x over inference-only and expert-iteration baselines. We show that performance scales with the number of generated questions and training iterations, and through ablations identify formal verification and difficulty-aware proposal as essential ingredients for successful self-play.

------------------------------------------------------------------------

21\. · 98% match · 2025 · 6.6 cit/yr\
**GAR: Generative Adversarial Reinforcement Learning for Formal Theorem Proving** ([link](https://doi.org/10.48550/arXiv.2510.11769))\
Ruida Wang, Jiarui Yao, Rui Pan, Shizhe Diao, and Tong Zhang\
*ArXiv* · Oct 13, 2025 · 5 citations

> Solving math problems through verifiable languages such as Lean has significantly impacted both the mathematics and computer science communities. Current state-of-the-art models are often trained with expensive online Reinforcement Learning (RL) or expert iteration. However, these approaches rely on fixed problem sets, which causes inefficient training and limits the model to tackle complex problems. To overcome these limitations, we propose **GAR**: *Generative Adversarial Reinforcement learning*, a comprehensive RL training framework that jointly trains the problem composer and solver in an adversarial loop. **GAR** introduces an implicit curriculum learning mechanism, which aligns task difficulty with the prover’s evolving capability. It thereby improves the training efficiency and enables stronger performance of proving advanced theorems. Experiments show that with **GAR** training, Goedel-Prover-V2-8B and DeepSeek-Prover-V2-7B achieve an average relative improvement in pass@32 of **4.20%** on MiniF2F-Test benchmark, while DeepSeek-Prover-V2’s pass@32 on ProofNet-Test increases from 22.58% to **25.81%**. Beyond formal proving, **GAR** establishes a general RL paradigm for co-evolution of problem generation and solving under verifiable environments. The training code for this paper is open-sourced in https://github.com/RickySkywalker/GAR-Official

------------------------------------------------------------------------

22\. · 97% match · 2026\
**ANCORA: Learning to Question via Manifold-Anchored Self-Play for Verifiable Reasoning** ([link](https://doi.org/10.48550/arXiv.2604.27644))\
Chengcao Yang and Jun Chen\
*ArXiv* · Apr 30, 2026 · 0 citations

> We propose a paradigm shift toward open-ended curriculum self-play: rather than learning to answer on a fixed prompt set, a unified policy learns to question: generating verifiable problems, solving them, and turning verifier feedback into self-improvement without human-annotated solutions. We introduce ANCORA, in which the policy alternates between a Proposer that synthesizes novel specifications and a Solver that produces verified solutions, anchored by three load-bearing mechanisms: a two-level group-relative update coupling Proposer advantages across specifications with Solver advantages across solution attempts; iterative self-distilled SFT projecting the base model onto its valid-output manifold before RL; and a UCB-guided Curriculum DAG whose policy-induced problem set can provably expand under self-composition. Without these stabilizers, sparse verifier feedback drives Proposer collapse even under MLRL-aligned rewards; with them, ANCORA bootstraps a verifiable curriculum from zero human solutions. Instantiated in Verus, ANCORA lifts Dafny2Verus pass@1 from a 26.6% SFT baseline to 81.5% in test-time training (TTT, 0-shot), outperforming PSV self-play by 15.8 points despite PSV’s 1-shot inference; in a transfer setting, training from Dafny2Verus seeds yields 36.2% and 17.2% pass@1 on held-out MBPP and HumanEval.

------------------------------------------------------------------------

23\. · 96% match · 2026\
**PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play** ([link](https://www.semanticscholar.org/paper/4fe61ff9df9714770be1fafa688b4591d07b807a))\
Roger Creus Castanyer et al.\
May 16, 2026 · 0 citations

> We introduce PopuLoRA, a population-based asymmetric self-play framework for reinforcement learning with verifiable rewards (RLVR) post-training of LLMs. Teachers and students are specialised LoRA adapters on a shared frozen base: teachers propose problems, matched students solve them under a programmatic verifier, and cross-evaluation between sub-populations replaces the self-calibration that limits single-agent self-play. A family of LoRA weight-space evolution operators (mutations and crossovers that produce same-rank population members in seconds) serves as the replacement step of a population-based training loop at 7B scale. We instantiate PopuLoRA on top of Absolute Zero Reasoner and compare it against a per-adapter compute-matched single-agent baseline. Where the single agent self-calibrates to generating easy problems it can reliably solve, the population enters a co-evolutionary arms race: teachers produce increasingly complex problems, student solve rates oscillate, and problem-space coverage keeps expanding throughout training. Despite lower training-time reward, the population mean outperforms the baseline on three code benchmarks (HumanEval+, MBPP+, LiveCodeBench) and seven math benchmarks (AIME 24/25, AMC 23, MATH-500, Minerva, GSM8K, OlympiadBench), and even the weakest member of the population beats the baseline on aggregate.

------------------------------------------------------------------------

24\. · 95% match · 2025 · 35 cit/yr\
**Algorithm Discovery With LLMs: Evolutionary Search Meets Reinforcement Learning** ([link](https://doi.org/10.48550/arXiv.2504.05108))\
Anja Surina et al.\
*ArXiv* · Apr 7, 2025 · 45 citations

> Discovering efficient algorithms for solving complex problems has been an outstanding challenge in mathematics and computer science, requiring substantial human expertise over the years. Recent advancements in evolutionary search with large language models (LLMs) have shown promise in accelerating the discovery of algorithms across various domains, particularly in mathematics and optimization. However, existing approaches treat the LLM as a static generator, missing the opportunity to update the model with the signal obtained from evolutionary exploration. In this work, we propose to augment LLM-based evolutionary search by continuously refining the search operator - the LLM - through reinforcement learning (RL) fine-tuning. Our method leverages evolutionary search as an exploration strategy to discover improved algorithms, while RL optimizes the LLM policy based on these discoveries. Our experiments on combinatorial optimization tasks demonstrate that integrating RL with evolutionary search accelerates the discovery of superior algorithms, showcasing the potential of RL-enhanced evolutionary strategies for algorithm design.

------------------------------------------------------------------------

25\. · 94% match · 2025 · 22 cit/yr\
**CALM: Co-evolution of Algorithms and Language Model for Automatic Heuristic Design** ([link](https://doi.org/10.48550/arXiv.2505.12285))\
Ziyao Huang, Weiwei Wu, Kui Wu, Jianping Wang, and Wei-Bin Lee\
*ArXiv* · May 18, 2025 · 26 citations

> Tackling complex optimization problems often relies on expert-designed heuristics, typically crafted through extensive trial and error. Recent advances demonstrate that large language models (LLMs), when integrated into well-designed evolutionary search frameworks, can autonomously discover high-performing heuristics at a fraction of the traditional cost. However, existing approaches predominantly rely on verbal guidance, i.e., manipulating the prompt generation process, to steer the evolution of heuristics, without adapting the underlying LLM. We propose a hybrid framework that combines verbal and numerical guidance, the latter achieved by fine-tuning the LLM via reinforcement learning based on the quality of generated heuristics. This joint optimization allows the LLM to co-evolve with the search process. Our method outperforms state-of-the-art (SOTA) baselines across various optimization tasks, running locally on a single 24GB GPU using a 7B model with INT4 quantization. It surpasses methods that rely solely on verbal guidance, even when those use significantly more powerful API-based models.

------------------------------------------------------------------------

26\. · 94% match · 2026 · 4.0 cit/yr\
**Poly-EPO: Training Exploratory Reasoning Models** ([link](https://doi.org/10.48550/arXiv.2604.17654))\
Ifdita Hasan Orney et al.\
*ArXiv* · Apr 19, 2026 · 2 citations

> Exploration is a cornerstone of learning from experience: it enables agents to find solutions to complex problems, generalize to novel ones, and scale performance with test-time compute. In this paper, we present a framework for post-training language models (LMs) that explicitly encourages optimistic exploration and promotes a synergy between exploration and exploitation. The central idea is to train the LM to generate sets of responses that are collectively accurate under the reward function and exploratory in their reasoning strategies. We first develop a general recipe for optimizing LMs with set reinforcement learning (set RL) under arbitrary objective functions, showing how standard RL algorithms can be adapted to this setting through a modification to the advantage computation. We then propose Polychromic Exploratory Policy Optimization (Poly-EPO), which instantiates this framework with an objective that explicitly synergizes exploration and exploitation. Across a range of reasoning benchmarks, we show that Poly-EPO improves generalization, as evidenced by higher pass@$`k`$ coverage, preserves greater diversity in model generations, and effectively scales with test-time compute.

------------------------------------------------------------------------

27\. · 93% match · 2026\
**When RL Suppresses Its Own Vocabulary: Recovering Reasoning Diversity in Puzzle-to-Math Transfer** ([link](https://www.semanticscholar.org/paper/d8d6ff9edbf7a975253115e28a45e98701c5c2d8))\
Mayug Maniparambil, Arjun Karuvally, Terrence J. Sejnowski, and Fergal Reid\
May 28, 2026 · 0 citations

> Reinforcement learning using verifiable rewards (RLVR) improves LLM reasoning, but the conditions under which it transfers across domains – and why it does so – remain under-explored. We study cross-domain transfer in a 7B model whose SFT and RL post-training stages use only constraint-satisfaction puzzles, with no mathematics problems in the post-training data. To analyze how transfer emerges, we introduce a reasoning primitive-level framework that combines a 9-class span classifier with motif extraction, allowing us to segment chain-of-thought traces into primitive motifs and track their evolution across training stages and domains. We find that puzzle SFT induces a reasoning-primitive vocabulary, yielding a $`+7`$pp \texttt{pass@32} gain on OlymMATH-Hard. Vanilla GSPO then composes these primitives into longer compute-verify chains, adding a further $`+6`$pp. However, this RL stage also suppresses exploratory primitives such as \textit{hypothesize} and \textit{backtrack}. To address this, we introduce a novelty bonus that rewards diverse correct rollouts, using perplexity under the reference model as a signal. This restores recovery primitives during RL and adds a further $`+7`$pp \texttt{pass@32} relative to vanilla GSPO. Finally, the end-to-end recipe raises the hard-math capability ceiling from $`16.0\%`$ at the OLMo3-7B-Instruct-SFT base to $`36.0\%`$, without adding any mathematics problems during the SFT or RL stages.

------------------------------------------------------------------------

28\. · 93% match · 2026\
**Breaking $`\textit{Winner-Takes-All}`$: Cooperative Policy Optimization Improves Diverse LLM Reasoning** ([link](https://www.semanticscholar.org/paper/75222439892a2fe50d3d0390795203364cc34040))\
Haoxuan Chen, Tianming Liang, Wei-Shi Zheng, and Jian-Fang Hu\
May 12, 2026 · 0 citations

> Reinforcement learning with verifiers (RLVR) has become a central paradigm for improving LLM reasoning, yet popular group-based optimization algorithms like GRPO often suffer from exploration collapse, where the models prematurely converge on a narrow set of high-scoring patterns, lacking the ability to explore new solutions. Recent efforts attempt to alleviate this by adding entropy regularization or diversity bonus. However, these approaches do not change the \textit{winner-takes-all} nature, where rollouts still compete for individual advantage rather than cooperating for maximizing global diversity. In this work, we propose Group Cooperative Policy Optimization (GCPO), which shifts the training paradigm from rollout competition to team cooperation. Specifically, GCPO replaces independent rollout scoring with team-level credit assignment: a rollout is rewarded by how much it contributes to the team’s valid solution coverage, rather than its individual accuracy. This coverage is described as a determinant volume over reward-weighted semantic embeddings, where only correct and non-redundant rollouts contribute to this volume. During advantage estimation, GCPO redistributes the collective team reward to each single rollout according to its average marginal contribution to the team. This cooperative training paradigm routes optimization toward non-redundant correct reasoning paths. Experiments across multiple reasoning benchmarks demonstrate that GCPO significantly improves both reasoning accuracy and solution diversity over existing approaches. Code will be released at https://github.com/bradybuddiemarch/gcpo.

------------------------------------------------------------------------

29\. · 92% match · 2025 · 11 cit/yr\
**Random Policy Valuation is Enough for LLM Reasoning with Verifiable Rewards** ([link](https://doi.org/10.48550/arXiv.2509.24981))\
Haoran He et al.\
*ArXiv* · Sep 29, 2025 · 9 citations

> RL with Verifiable Rewards (RLVR) has emerged as a promising paradigm for improving the reasoning abilities of large language models (LLMs). Current methods rely primarily on policy optimization frameworks like PPO and GRPO, which follow generalized policy iteration that alternates between evaluating the current policy’s value and improving the policy based on evaluation. While effective, they often suffer from training instability and diversity collapse, requiring complex heuristic tricks and careful tuning. We observe that standard RLVR in math reasoning can be formalized as a specialized finite-horizon Markov Decision Process with deterministic state transitions, tree-structured dynamics, and binary terminal rewards. Though large in scale, the underlying structure is simpler than general-purpose control settings for which popular RL algorithms (e.g., PPO) were developed, suggesting that several sophisticated techniques in existing methods may be reduced or even omitted. Based on this insight, we prove a surprising result: the optimal action can be recovered from the Q-function of a fixed uniformly random policy, thereby bypassing the generalized policy iteration loop and its associated heuristics. We introduce Random Policy Valuation for Diverse Reasoning (ROVER) to translate this principle into a practical and scalable algorithm for LLM math reasoning, a minimalist yet highly effective RL method that samples actions from a softmax over these uniform-policy Q-values. ROVER preserves diversity throughout training, allowing sustained exploration of multiple valid pathways. Across multiple base models and standard math reasoning benchmarks, ROVER demonstrates superior performance in both \textbf{quality} (\textbf{+8.2} on pass@1, \textbf{+16.8} on pass@256) and \textbf{diversity} (\textbf{+17.6%}), despite its radical simplification compared to strong, complicated existing methods.

------------------------------------------------------------------------

30\. · 91% match · 2025 · 20 cit/yr\
**Differential Smoothing Mitigates Sharpening and Improves LLM Reasoning** ([link](https://doi.org/10.48550/arXiv.2511.19942))\
Jingchu Gai, Guanning Zeng, Huaqing Zhang, and Aditi Raghunathan\
*ArXiv* · Nov 25, 2025 · 13 citations

> It is widely recognized that reinforcement learning (RL) fine-tuning of large language models often leads to diversity collapse, where outputs lack variety. Prior work has proposed a range of heuristics to counteract this effect, but these methods are ad hoc: they frequently trade off correctness for diversity, their effectiveness varies across tasks, and in some cases they even contradict one another. In this work, we place these observations on a rigorous foundation. We first provide a formal proof of why RL fine-tuning exhibits diversity collapse via a selection and reinforcement bias. Next, we make a key observation that any reward modification to address diversity collapse only needs to be applied on the correct trajectories. Building directly on this analysis, we introduce a principled method – differential smoothing – that provably improves both correctness and diversity, outperforming vanilla RL as well as widely used entropy-based heuristics. Our theory precisely characterizes when existing heuristics help and why they fail, while showing that differential smoothing is universally superior. Extensive experiments with models from 1B to 7B parameters, across domains including CountDown and real-world mathematical reasoning, demonstrate consistent gains. Differential smoothing improves both Pass@1 and Pass@k, with up to 6.7% improvements on AIME24 dataset.

------------------------------------------------------------------------

31\. · 91% match · 2025 · 41 cit/yr\
**Unlocking Exploration in RLVR: Uncertainty-aware Advantage Shaping for Deeper Reasoning** ([link](https://doi.org/10.48550/arXiv.2510.10649))\
Can Xie et al.\
*ArXiv* · Oct 12, 2025 · 31 citations

> Reinforcement Learning with Verifiable Rewards (RLVR) has shown significant promise for enhancing the reasoning capabilities of large language models (LLMs). However, prevailing algorithms like GRPO broadcast a uniform advantage signal across all tokens in a sequence. This coarse-grained approach overlooks the pivotal role of uncertain, high-stakes decisions during reasoning, leading to inefficient exploration and the well-documented problem of entropy collapse. To address this, we introduce UnCertainty-aware Advantage Shaping (UCAS), a model-free method that refines credit assignment by leveraging the model’s internal uncertainty signals. UCAS operates in two stages: it first modulates the response-level advantage using a logit-space self-confidence proxy, and then applies an asymmetric token-level penalty based on raw logit certainty. This dual mechanism encourages exploration of high-uncertainty paths that yield correct answers while penalizing overconfident yet erroneous reasoning, effectively balancing the exploration-exploitation trade-off. Extensive experiments on five mathematical reasoning benchmarks show that UCAS significantly outperforms strong RLVR baselines across multiple model scales, including 1.5B and 7B. Our analysis confirms that UCAS not only achieves higher rewards but also promotes greater reasoning diversity and successfully mitigates entropy collapse. Code is available at https://github.com/xvolcano02/UCAS.

------------------------------------------------------------------------

32\. · 90% match · 2026\
**Uniform-Correct Policy Optimization: Breaking RLVR’s Indifference to Diversity** ([link](https://www.semanticscholar.org/paper/e3b2d3d1a8cf1a6f74748455df21dfc955fefea9))\
Anamika Lochab, Bolian Li, and Ruqi Zhang\
May 1, 2026 · 0 citations

> Reinforcement Learning with Verifiable Rewards (RLVR) has achieved substantial gains in single-attempt accuracy (Pass@1) on reasoning tasks, yet often suffers from reduced multi-sample coverage (Pass@K), indicating diversity collapse. We identify a structural cause for this degradation: common RLVR objectives, such as GRPO, are indifferent to how probability mass is distributed among correct solutions. Combined with stochastic training dynamics, this indifference induces a self-reinforcing collapse, in which probability mass concentrates on a narrow subset of correct outputs while alternative valid solutions are suppressed. We formalize this collapse mechanism and further characterize the optimal policy structure under two complementary criteria: robustness and entropy-regularized optimality, which identify the Uniform-Correct Policy as uniquely optimal. Motivated by this analysis, we propose Uniform-Correct Policy Optimization (UCPO), a modification to GRPO that adds a conditional uniformity penalty on the policy’s distribution over correct solutions. The penalty redistributes gradient signal toward underrepresented correct responses, encouraging uniform allocation of probability mass within the correct set. Across three models (1.5B-7B parameters) and five mathematical reasoning benchmarks, UCPO improves Pass@K and diversity while maintaining competitive Pass@1, achieving up to +10% absolute improvement on AIME24 at Pass@64 and up to 45% higher equation-level diversity within the correct set. The code is available at https://github.com/AnamikaLochab/UCPO.

------------------------------------------------------------------------

33\. · 90% match · 2025 · 19 cit/yr\
**Improving RL Exploration for LLM Reasoning through Retrospective Replay** ([link](https://doi.org/10.48550/arXiv.2504.14363))\
Shihan Dou et al.\
*ArXiv* · Apr 19, 2025 · 24 citations

> Reinforcement learning (RL) has increasingly become a pivotal technique in the post-training of large language models (LLMs). The effective exploration of the output space is essential for the success of RL. We observe that for complex problems, during the early stages of training, the model exhibits strong exploratory capabilities and can identify promising solution ideas. However, its limited capability at this stage prevents it from successfully solving these problems. The early suppression of these potentially valuable solution ideas by the policy gradient hinders the model’s ability to revisit and re-explore these ideas later. Consequently, although the LLM’s capabilities improve in the later stages of training, it still struggles to effectively address these complex problems. To address this exploration issue, we propose a novel algorithm named Retrospective Replay-based Reinforcement Learning (RRL), which introduces a dynamic replay mechanism throughout the training process. RRL enables the model to revisit promising states identified in the early stages, thereby improving its efficiency and effectiveness in exploration. To evaluate the effectiveness of RRL, we conduct extensive experiments on complex reasoning tasks, including mathematical reasoning and code generation, and general dialogue tasks. The results indicate that RRL maintains high exploration efficiency throughout the training period, significantly enhancing the effectiveness of RL in optimizing LLMs for complicated reasoning tasks. Moreover, it also improves the performance of RLHF, making the model both safer and more helpful.

------------------------------------------------------------------------

34\. · 90% match · 2026\
**Cast a Wider Net: Coordinated Pass@K Policy Optimization for Code Reasoning** ([link](https://www.semanticscholar.org/paper/24ed88680bbf7256746a6e6995ff9a86817b56fe))\
Yilong Li, Suman Banerjee, and Tong Che\
May 26, 2026 · 0 citations

> Repeated sampling with a verifier is the standard way to allocate test-time compute for code generation, with pass@$`K`$ as the canonical metric. Yet the standard policy class draws $`K`$ independent samples from a single answer distribution, so attempts often collapse onto near-duplicate reasoning paths and waste the budget on redundant rollouts. This failure is costly in competitive programming, where many problems admit multiple distinct algorithmic strategies and pass@$`K`$ requires only one correct attempt. We propose Coordinated Pass@$`K`$ Policy Optimization (CPPO), which turns pass@$`K`$ generation into joint exploration over strategies: a planner emits a tuple of $`K{=}4`$ alternative high-level methods, and a shared solver attempts one solution per method. CPPO trains this joint policy with a multiplicative planner reward, $`R_{\mathrm{plan}} = J_\psi \cdot R_{\mathrm{out}}`$, assigning credit only to valid strategy tuples that lead to verifier-confirmed pass@$`K`$ success. Across APPS, CodeContests, and LiveCodeBench-v6, CPPO improves pass@$`4`$ over direct sampling, planning baselines, planner-only SFT, and pass@$`K`$-oriented RL under the same $`K{=}4`$ solver-attempt budget, with statistically significant gains on six of nine model–benchmark cells. The largest single gain is $`+0.16`$ on Qwen3.5-9B LiveCodeBench-v6 over the strongest baseline, PKPO ($`0.588 \rightarrow 0.748`$; paired bootstrap, $`p<0.05`$).

------------------------------------------------------------------------

35\. · 89% match · 2026\
**Beyond pass@k: Redundancy-Aware RLVR for Multi-Sample Code Generation** ([link](https://www.semanticscholar.org/paper/a16b15ae619e0ba0560027e7746aa3ae03af5157))\
Lecadre Florian, Alexandre Verine, Rio Yokota, and Benjamin Négrevergne\
May 27, 2026 · 0 citations

> LLMs for code generation are commonly evaluated in repeated-sampling settings using Pass@k, where multiple candidate programs are executed against unit tests under a finite sampling budget. While recent verifier-based reinforcement learning (RLVR) methods improve executable correctness, how these objectives affect redundancy among sampled programs remains poorly understood. In this work, we study implementation-level redundancy in code generation using JPlag, a plagiarism-detection system for code. Across models and benchmarks, we show that correctness-only RLVR often concentrates generations around repeated implementations, whereas Pass@k-aware objectives maintain lower redundancy and improve larger-budget performance. Motivated by these observations, we augment RLVR with direct anti-redundancy rewards based on JPlag similarity. Across 3 models and 3 benchmarks, discouraging near-duplicate generations reliably improves finite-budget executable performance, often matching or outperforming specialized Pass@k-aware objectives.

------------------------------------------------------------------------

36\. · 87% match · 2026 · 9.6 cit/yr\
**Reinforced Efficient Reasoning via Semantically Diverse Exploration** ([link](https://doi.org/10.48550/arXiv.2601.05053))\
Ziqi Zhao et al.\
*ArXiv* · Jan 8, 2026 · 5 citations

> Reinforcement learning with verifiable rewards (RLVR) has proven effective in enhancing the reasoning of large language models (LLMs). Monte Carlo Tree Search (MCTS)-based extensions improve upon vanilla RLVR (e.g., GRPO) by providing tree-based reasoning rollouts that enable fine-grained and segment-level credit assignment. However, existing methods still suffer from limited exploration diversity and inefficient reasoning. To address the above challenges, we propose reinforced efficient reasoning via semantically diverse explorations, i.e., ROSE, for LLMs. To encourage more diverse reasoning exploration, our method incorporates a semantic-entropy-based branching strategy and an $`\varepsilon`$-exploration mechanism. The former operates on already sampled reasoning rollouts to capture semantic uncertainty and select branching points with high semantic divergence to generate new successive reasoning paths, whereas the latter stochastically initiates reasoning rollouts from the root, preventing the search process from becoming overly local. To improve efficiency, we design a length-aware segment-level advantage estimator that rewards concise and correct reasoning while penalizing unnecessarily long reasoning chains. Extensive experiments on various mathematical reasoning benchmarks with Qwen and Llama models validate the effectiveness and efficiency of ROSE. Codes are available at https://github.com/ZiqiZhao1/ROSE-rl.

------------------------------------------------------------------------

37\. · 86% match · 2026 · 6.0 cit/yr\
**Learning to Explore with Parameter-Space Noise: A Deep Dive into Parameter-Space Noise for Reinforcement Learning with Verifiable Rewards** ([link](https://doi.org/10.48550/arXiv.2602.02555))\
Bizhe Bai, Xinyue Wang, Peng Ye, and Tao Chen\
*ArXiv* · Jan 30, 2026 · 3 citations

> Reinforcement Learning with Verifiable Rewards (RLVR) improves LLM reasoning, yet growing evidence indicates an exploration ceiling: it often reweights existing solution traces rather than discovering new strategies, limiting gains under large sampling budgets (e.g., pass-at-256). We address this limitation with PSN-RLVR, which perturbs policy parameters before rollout generation to induce temporally consistent, trajectory-level exploration that better preserves long-horizon chain-of-thought coherence than action-space noise. To mitigate the resulting sampling-update mismatch, we incorporate truncated importance sampling (TIS). To avoid expensive KL-based adaptive noise control, we propose a computationally efficient real-time adaptive noise scheduler driven by a lightweight surrogate that combines semantic diversity with normalized self-certainty. Instantiated on GRPO, a widely used RLVR method, PSN-GRPO consistently expands the effective reasoning capability boundary across multiple mathematical reasoning benchmarks and model families, yielding higher pass-at-k under large sampling budgets and outperforming prior exploration-oriented RLVR methods (e.g., Pass-at-k-style training) while remaining orthogonal and thus composable for additional gains.

------------------------------------------------------------------------

38\. · 85% match · 2026\
**Deep Dense Exploration for LLM Reinforcement Learning via Pivot-Driven Resampling** ([link](https://doi.org/10.48550/arXiv.2602.14169))\
Yiran Guo et al.\
*ArXiv* · Feb 15, 2026 · 0 citations

> Effective exploration is a key challenge in reinforcement learning for large language models: discovering high-quality trajectories within a limited sampling budget from the vast natural language sequence space. Existing methods face notable limitations: GRPO samples exclusively from the root, saturating high-probability trajectories while leaving deep, error-prone states under-explored. Tree-based methods blindly disperse budgets across trivial or unrecoverable states, causing sampling dilution that fails to uncover rare correct suffixes and destabilizes local baselines. To address this, we propose Deep Dense Exploration (DDE), a strategy that focuses exploration on $`\textit{pivots}`$-deep, recoverable states within unsuccessful trajectories. We instantiate DDE with DEEP-GRPO, which introduces three key innovations: (1) a lightweight data-driven utility function that automatically balances recoverability and depth bias to identify pivot states; (2) local dense resampling at each pivot to increase the probability of discovering correct subsequent trajectories; and (3) a dual-stream optimization objective that decouples global policy learning from local corrective updates. Experiments on mathematical reasoning benchmarks demonstrate that our method consistently outperforms GRPO, tree-based methods, and other strong baselines. Code is available at https://github.com/AgentCombo/DEEP-GRPO

------------------------------------------------------------------------

39\. · 84% match · 2025 · 11 cit/yr\
**Lookahead Tree-Based Rollouts for Enhanced Trajectory-Level Exploration in Reinforcement Learning with Verifiable Rewards** ([link](https://doi.org/10.48550/arXiv.2510.24302))\
Shangyu Xing, Siyuan Wang, Chenyuan Yang, Xinyu Dai, and Xiang Ren\
*ArXiv* · Oct 28, 2025 · 8 citations

> Reinforcement Learning with Verifiable Rewards (RLVR), particularly with algorithms like Group Relative Policy Optimization (GRPO), has proven highly effective in enhancing the reasoning capabilities of large language models. However, a critical bottleneck in current pipelines lies in the limited diversity of sampled trajectories during group rollouts. Homogeneous trajectories and their associated rewards would diminish the return signals for policy updates, thereby hindering effective policy learning. This lack of diversity stems primarily from token-level stochastic sampling, where local variations are likely to collapse into near-identical reasoning paths. To address this limitation, we propose Lookahead Tree-Based Rollouts (LATR), a novel rollout strategy designed to explicitly promotes trajectory-level diversity by enforcing branching into different candidate tokens likely to yield distinct continuations. Specifically, LATR iteratively operates in three stages: (1) branching at high-uncertainty generation steps, (2) performing lookahead simulation for each new branch, and (3) pruning branches that exhibits prolonged similarity during simulation. Compared with stochastic Sampling, LATR accelerates policy learning by 131% on average and improves final pass@1 performance by 4.2% on both GRPO and Dynamic sAmpling Policy Optimization (DAPO) algorithms across different reasoning tasks. Our code and data are publicly available at https://github.com/starreeze/latr.

------------------------------------------------------------------------

40\. · 84% match · 2026 · 2.0 cit/yr\
**How You Begin is How You Reason: Driving Exploration in RLVR via Prefix-Tuned Priors** ([link](https://www.semanticscholar.org/paper/78f8f1358752e26cac98016e1ee2c4a75cf3fb39))\
Yifan Xu, Junren Chen, and Yifan Chen\
May 9, 2026 · 1 citations

> Reinforcement learning with verifiable rewards (RLVR) recently thrives in large language model (LLM) reasoning tasks. However, the reward sparsity and the long reasoning horizon make effective exploration challenging. In practice, this challenge manifests as the \emph{entropy collapse} phenomenon, where RLVR improves single-rollout accuracy but fails to expand coverage on successful reasoning trajectories. Passive exploration techniques like entropy regularization tend to dismiss generation quality, resulting in noisy rollouts. In response to this issue, we propose an Information-Maximizing Augmented eXploration (IMAX) framework to train a pool of soft prefixes that reshapes the base model’s prior over reasoning trajectories. Rather than relying on RL to incentivize exploration on top of the base model, each prefix acts as a trainable control knob that induces a distinct rollout distribution from the same backbone model. To encourage discovery of diverse and task-relevant reasoning behaviors, we derive an Information Maximization (InfoMax) reward to complement the verifiable rewards for RL training. IMAX is in general algorithm-agnostic and can be seamlessly integrated into existing RLVR pipelines. Experiment results have shown that across three backbone scales, IMAX consistently improves reasoning performance over standard RLVR, with gains up to 11.60% in Pass@4 and 10.57% in Avg@4.

------------------------------------------------------------------------

41\. · 83% match · 2026 · 14 cit/yr\
**DSDR: Dual-Scale Diversity Regularization for Exploration in LLM Reasoning** ([link](https://doi.org/10.48550/arXiv.2602.19895))\
Zhongwei Wan et al.\
*ArXiv* · Feb 23, 2026 · 7 citations

> Reinforcement learning with verifiers (RLVR) is a central paradigm for improving large language model (LLM) reasoning, yet existing methods often suffer from limited exploration. Policies tend to collapse onto a few reasoning patterns and prematurely stop deep exploration, while conventional entropy regularization introduces only local stochasticity and fails to induce meaningful path-level diversity, leading to weak and unstable learning signals in group-based policy optimization. We propose DSDR, a Dual-Scale Diversity Regularization reinforcement learning framework that decomposes diversity in LLM reasoning into global and coupling components. Globally, DSDR promotes diversity among correct reasoning trajectories to explore distinct solution modes. Locally, it applies a length-invariant, token-level entropy regularization restricted to correct trajectories, preventing entropy collapse within each mode while preserving correctness. The two scales are coupled through a global-to-local allocation mechanism that emphasizes local regularization for more distinctive correct trajectories. We provide theoretical support showing that DSDR preserves optimal correctness under bounded regularization, sustains informative learning signals in group-based optimization, and yields a principled global-to-local coupling rule. Experiments on multiple reasoning benchmarks demonstrate consistent improvements in accuracy and pass@k, highlighting the importance of dual-scale diversity for deep exploration in RLVR. Code is available at https://github.com/SUSTechBruce/DSDR.

------------------------------------------------------------------------

42\. · 83% match · 2026 · 4.0 cit/yr\
**Leveraging Error Diversity in Group Rollouts for Reinforcement Learning** ([link](https://www.semanticscholar.org/paper/0398c4b3f10abfff1db33948ff8f16be1c119d98))\
Wenpu Liu et al.\
May 17, 2026 · 2 citations

> Reinforcement Learning from Verifiable Rewards (RLVR) typically samples multiple responses per prompt and assigns binary rewards based on individual correctness, yet the collective structure of the group output, specifically the distribution of errors, is largely discarded. We identify this as a missed opportunity: empirical analysis reveals that error diversity within a group is a strong predictor of training success, with problems eliciting diverse wrong answers benefiting substantially more from RLVR than those producing homogeneous failures. Motivated by this observation, we propose Error Diversity Advantage Shaping (EDAS), a lightweight, algorithm-agnostic technique that modulates the advantage signal for incorrect rollouts based on intra-group error diversity. EDAS amplifies penalties for dominant, repeated errors and attenuates penalties for rare, exploratory ones, thereby encouraging the model to maintain diverse reasoning paths and discouraging error perseveration. Crucially, EDAS operates as a simple post-hoc adjustment that can be seamlessly integrated into any RLVR algorithm. We validate EDAS on top of several mainstream RLVR methods across a series of models and seven challenging math benchmarks, demonstrating consistent improvements. Notably, EDAS yields an average improvement of 6.29 points over DAPO on Qwen3-8B across seven benchmarks, confirming that exploiting the latent information in group rollouts is a broadly effective strategy for strengthening RLVR.

------------------------------------------------------------------------

43\. · 82% match · 2025 · 16 cit/yr\
**Can LLMs Guide Their Own Exploration? Gradient-Guided Reinforcement Learning for LLM Reasoning** ([link](https://doi.org/10.48550/arXiv.2512.15687))\
Zhenwen Liang et al.\
*ArXiv* · Dec 17, 2025 · 9 citations

> Reinforcement learning has become essential for strengthening the reasoning abilities of large language models, yet current exploration mechanisms remain fundamentally misaligned with how these models actually learn. Entropy bonuses and external semantic comparators encourage surface level variation but offer no guarantee that sampled trajectories differ in the update directions that shape optimization. We propose G2RL, a gradient guided reinforcement learning framework in which exploration is driven not by external heuristics but by the model own first order update geometry. For each response, G2RL constructs a sequence level feature from the model final layer sensitivity, obtainable at negligible cost from a standard forward pass, and measures how each trajectory would reshape the policy by comparing these features within a sampled group. Trajectories that introduce novel gradient directions receive a bounded multiplicative reward scaler, while redundant or off manifold updates are deemphasized, yielding a self referential exploration signal that is naturally aligned with PPO style stability and KL control. Across math and general reasoning benchmarks (MATH500, AMC, AIME24, AIME25, GPQA, MMLUpro) on Qwen3 base 1.7B and 4B models, G2RL consistently improves pass@1, maj@16, and pass@k over entropy based GRPO and external embedding methods. Analyzing the induced geometry, we find that G2RL expands exploration into substantially more orthogonal and often opposing gradient directions while maintaining semantic coherence, revealing that a policy own update space provides a far more faithful and effective basis for guiding exploration in large language model reinforcement learning.

------------------------------------------------------------------------

44\. · 82% match · 2025 · 55 cit/yr\
**Rethinking Entropy Interventions in RLVR: An Entropy Change Perspective** ([link](https://doi.org/10.48550/arXiv.2510.10150))\
Zhezheng Hao et al.\
*ArXiv* · Oct 11, 2025 · 42 citations

> Reinforcement Learning with Verifiable Rewards (RLVR) serves as a cornerstone technique for enhancing the reasoning capabilities of Large Language Models (LLMs). However, its training is often plagued by \emph{entropy collapse}, a rapid decline in policy entropy that limits exploration and undermines training effectiveness. While recent works attempt to mitigate this issue via several heuristic entropy interventions, the underlying mechanisms remain poorly understood. In this work, we conduct comprehensive theoretical and empirical analyses of entropy dynamics in RLVR, offering two main insights: (1) We derive a tight analytical approximation for token-level entropy change at each update step, revealing four governing factors and providing a unified theoretical framework to explain how existing methods influence entropy; (2) We reveal a fundamental limitation of recent approaches: they rely on heuristic adjustments to one or two of these factors, leaving other relevant factors unconsidered, thus inherently limiting their effectiveness. Motivated by these findings, we propose STEER, a principled entropy-modulation method that adaptively reweights tokens based on theoretically-estimated entropy variations. Extensive experiments across six mathematical reasoning and three coding benchmarks demonstrate that STEER effectively mitigates entropy collapse and consistently outperforms state-of-the-art baselines.

------------------------------------------------------------------------

45\. · 82% match · 2025 · 19 cit/yr\
**XRPO: Pushing the limits of GRPO with Targeted Exploration and Exploitation** ([link](https://doi.org/10.48550/arXiv.2510.06672))\
Udbhav Bamba, Minghao Fang, Yifan Yu, Haizhong Zheng, and Fan Lai\
*ArXiv* · Oct 8, 2025 · 15 citations

> Reinforcement learning algorithms such as GRPO have driven recent advances in large language model (LLM) reasoning. While scaling the number of rollouts stabilizes training, existing approaches suffer from limited exploration on challenging prompts and leave informative feedback signals underexploited, due to context-independent rollout allocation across prompts (e.g., generating 16 rollouts per prompt) and relying heavily on sparse rewards. This paper presents XRPO(eXplore - eXploit GRPO), a unified framework that recasts policy optimization through the principled lens of rollout exploration-exploitation. To enhance exploration, XRPO introduces a mathematically grounded rollout allocator that adaptively prioritizes prompts with higher potential for uncertainty reduction. It further addresses stagnation on zero-reward prompts through an in-context seeding strategy that injects curated exemplars, steering the model into more difficult reasoning trajectories. To strengthen exploitation, XRPO develops a group-relative, novelty-aware advantage sharpening mechanism that leverages sequence likelihoods to amplify low-probability yet correct responses, thereby extending the policy’s reach beyond sparse rewards. Experiments across diverse math and coding benchmarks on both reasoning and non-reasoning models demonstrate that XRPO outperforms existing advances (e.g., GRPO and GSPO) up to 4% pass@1 and 6% cons@32, while accelerating training convergence by up to 2.7X.

------------------------------------------------------------------------

46\. · 80% match · 2025 · 9.2 cit/yr\
**Revisiting Entropy Regularization: Adaptive Coefficient Unlocks Its Potential for LLM Reinforcement Learning** ([link](https://doi.org/10.18653/v1/2026.findings-acl.895))\
Xiaoyun Zhang et al.\
*Findings of the Association for Computational Linguistics: ACL 2026* · Oct 13, 2025 · 7 citations

> Reasoning ability has become a defining capability of Large Language Models (LLMs), with Reinforcement Learning with Verifiable Rewards (RLVR) emerging as a key paradigm to enhance it. However, RLVR training often suffers from policy entropy collapse, where the policy becomes overly deterministic, hindering exploration and limiting reasoning performance. While entropy regularization is a common remedy, its effectiveness is highly sensitive to the fixed coefficient, making it unstable across tasks and models. In this work, we revisit entropy regularization in RLVR and argue that its potential has been largely underestimated. Our analysis shows that (i) tasks of varying difficulty demand distinct exploration intensities, and (ii) balanced exploration may require the policy entropy to be maintained within a moderate range below its initial level. Therefore, we propose Adaptive Entropy Regularization (AER)–a framework that dynamically balances exploration and exploitation via three components: difficulty-aware coefficient allocation, initial-anchored target entropy, and dynamic global coefficient adjustment. Experiments on multiple mathematical reasoning benchmarks show that AER consistently outperforms baselines, improving both reasoning accuracy and exploration capability.

------------------------------------------------------------------------

47\. · 80% match · 2025 · 341 cit/yr\
**The Entropy Mechanism of Reinforcement Learning for Reasoning Language Models** ([link](https://doi.org/10.48550/arXiv.2505.22617))\
Ganqu Cui et al.\
*ArXiv* · May 28, 2025 · 388 citations

> This paper aims to overcome a major obstacle in scaling RL for reasoning with LLMs, namely the collapse of policy entropy. Such phenomenon is consistently observed across vast RL runs without entropy intervention, where the policy entropy dropped sharply at the early training stage, this diminished exploratory ability is always accompanied with the saturation of policy performance. In practice, we establish a transformation equation R=-a\*e^H+b between entropy H and downstream performance R. This empirical law strongly indicates that, the policy performance is traded from policy entropy, thus bottlenecked by its exhaustion, and the ceiling is fully predictable H=0, R=-a+b. Our finding necessitates entropy management for continuous exploration toward scaling compute for RL. To this end, we investigate entropy dynamics both theoretically and empirically. Our derivation highlights that, the change in policy entropy is driven by the covariance between action probability and the change in logits, which is proportional to its advantage when using Policy Gradient-like algorithms. Empirical study shows that, the values of covariance term and entropy differences matched exactly, supporting the theoretical conclusion. Moreover, the covariance term stays mostly positive throughout training, further explaining why policy entropy would decrease monotonically. Through understanding the mechanism behind entropy dynamics, we motivate to control entropy by restricting the update of high-covariance tokens. Specifically, we propose two simple yet effective techniques, namely Clip-Cov and KL-Cov, which clip and apply KL penalty to tokens with high covariances respectively. Experiments show that these methods encourage exploration, thus helping policy escape entropy collapse and achieve better downstream performance.

------------------------------------------------------------------------

48\. · 79% match · 2025 · 2.8 cit/yr\
**Do Not Step Into the Same River Twice: Learning to Reason from Trial and Error** ([link](https://doi.org/10.48550/arXiv.2510.26109))\
Chenming Tang, Hsiu-Yuan Huang, Weijie Liu, Saiyong Yang, and Yunfang Wu\
*ArXiv* · Oct 30, 2025 · 2 citations

> Reinforcement learning with verifiable rewards (RLVR) has significantly boosted the reasoning capability of language models (LMs). However, existing RLVR approaches train LMs based on their own on-policy responses and are constrained by the initial capability of LMs, thus prone to exploration stagnation, in which LMs fail to solve more training problems and cannot further learn from the training data. Some approaches try to address this by leveraging off-policy solutions to training problems, but rely on external expert guidance that is limited in availability and scalability. In this work, we propose LTE (Learning to reason from Trial and Error), an approach that hints LMs with their previously self-made mistakes, not requiring any external expert guidance. Experiments validate the effectiveness of LTE, which outperforms the normal group relative policy optimization (GRPO) by 5.02 in Pass@1 and 9.96 in Pass@k on average across six mathematical reasoning benchmarks for Qwen3-8B-Base and even performs better than methods that require external guidance. Further analysis confirms that LTE successfully mitigates exploration stagnation and enhances both exploitation and exploration during training. Our code is available at https://github.com/JamyDon/LTE.

------------------------------------------------------------------------

49\. · 79% match · 2025 · 451 cit/yr\
**Beyond the 80/20 Rule: High-Entropy Minority Tokens Drive Effective Reinforcement Learning for LLM Reasoning** ([link](https://doi.org/10.48550/arXiv.2506.01939))\
Shenzhi Wang et al.\
*ArXiv* · Jun 2, 2025 · 506 citations

> Reinforcement Learning with Verifiable Rewards (RLVR) has emerged as a powerful approach to enhancing the reasoning capabilities of Large Language Models (LLMs), while its mechanisms are not yet well understood. In this work, we undertake a pioneering exploration of RLVR through the novel perspective of token entropy patterns, comprehensively analyzing how different tokens influence reasoning performance. By examining token entropy patterns in Chain-of-Thought (CoT) reasoning, we observe that only a small fraction of tokens exhibit high entropy, and these tokens act as critical forks that steer the model toward diverse reasoning pathways. Furthermore, studying how entropy patterns evolve during RLVR training reveals that RLVR largely adheres to the base model’s entropy patterns, primarily adjusting the entropy of high-entropy tokens. These findings highlight the significance of high-entropy tokens (i.e., forking tokens) to RLVR. We ultimately improve RLVR by restricting policy gradient updates to forking tokens and uncover a finding even beyond the 80/20 rule: utilizing only 20% of the tokens while maintaining performance comparable to full-gradient updates on the Qwen3-8B base model and significantly surpassing full-gradient updates on the Qwen3-32B (+11.04 on AIME’25 and +7.71 on AIME’24) and Qwen3-14B (+4.79 on AIME’25 and +5.21 on AIME’24) base models, highlighting a strong scaling trend. In contrast, training exclusively on the 80% lowest-entropy tokens leads to a marked decline in performance. These findings indicate that the efficacy of RLVR primarily arises from optimizing the high-entropy tokens that decide reasoning directions. Collectively, our results highlight the potential to understand RLVR through a token-entropy perspective and optimize RLVR by leveraging high-entropy minority tokens to further improve LLM reasoning.

------------------------------------------------------------------------

50\. · 78% match · 2026 · 12 cit/yr\
**F-GRPO: Don’t Let Your Policy Learn the Obvious and Forget the Rare** ([link](https://doi.org/10.48550/arXiv.2602.06717))\
Daniil Plyusov et al.\
*ArXiv* · Feb 6, 2026 · 6 citations

> Reinforcement Learning with Verifiable Rewards (RLVR) is commonly based on group sampling to estimate advantages and stabilize policy updates. In practice, computational limits often rule out very large groups, so training proceeds with finite rollout sets that can reinforce only the correct behavior they expose. At practical group sizes, updates can miss rare-correct trajectories while still containing mixed rewards, concentrating probability on more common sampled solutions. We derive the probability of such prompt-local tail-miss events as a function of group size, showing non-monotonic behavior, and in the categorical abstraction characterize how unsampled-correct mass can shrink even as total correct mass grows. Motivated by this analysis, we propose a difficulty-aware scaling coefficient, inspired by Focal loss, that down-weights updates on high-success sampled groups. Empirically, categorical simulation illustrates the same effect in the categorical setting, Maze provides a single-solution test, and LLM experiments include a representative GRPO group-size sweep together with fixed-$`N`$ transfer across GRPO, DAPO, and CISPO. On Qwen2.5-7B at $`N{=}8`$, our method improves average math pass@256 from 64.1 $`\rightarrow`$ 70.3 (GRPO), 69.3 $`\rightarrow`$ 72.5 (DAPO), and 73.2 $`\rightarrow`$ 76.8 (CISPO); OOD pass@256 also improves in all three cases, without increasing group size or computational cost.

*Showing top 50 of 72 papers. Full details available via CSV or BibTeX export.*
