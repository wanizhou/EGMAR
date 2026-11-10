# 100 条 QA 审核明细
## 1/100 sc2qa_000752

原标签：`ambiguous`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** Can a Zergling attack an enemy unit when the target's ground-or-air status is unknown?

**原参考答案：** The Zergling can only attack ground units. Its weapon is explicitly restricted to ground targets, so the target's ground-or-air status must be clarified to determine whether the Zergling can engage.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 需澄清 | complete | ambiguous | high |
| B | 未发现实质问题 | 需澄清 | complete | ambiguous | high |
| C | 未发现实质问题 | 需澄清 | complete | ambiguous | high |

**A 的理由：** 跳虫只能攻击地面单位；目标层未给定时无法判定可否交战，答案准确识别这一缺失条件。

候选答案：A Zergling can attack only ground targets; the target layer must be known.

**B 的理由：** 小狗普通攻击只能对地；目标层未给定，因此只能给条件答案，参考答案正确指出这一点。歧义来自目标信息缺失，不等于推理深度增加。

候选答案：A Zergling can attack a ground target, but not an air target.

**C 的理由：** 虫狗只能对地；目标层级未给出时不能判断这一具体目标能否攻击，答案正确保留了条件。歧义来自目标信息缺失，不代表推理层数增加。

候选答案：A Zergling can attack the target only if it is a ground target.

## 2/100 sc2qa_000388

原标签：`ambiguous`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** Can the Terran Planetary Fortress attack air units?

**原参考答案：** The Planetary Fortress is explicitly defined with a ground-only target attribute. Its primary weapon is also configured to target only ground units. Therefore, it cannot attack air units unless the target layer is clarified to include air.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | complete | single_hop | high |
| B | 部分正确 | 有效 | not_applicable | single_hop | high |
| C | 部分正确 | 有效 | not_applicable | single_hop | high |

**A 的理由：** 行星要塞只能对地。末句的 unless 暗示把目标层说明为对空即可攻击，澄清目标属性不会改变要塞武器的对地限制。

候选答案：No. A Planetary Fortress can attack only ground targets.

**B 的理由：** 行星要塞的伊比克斯炮确实只能对地，但结尾把‘澄清目标层包含空中’写成可以攻击空军的例外；澄清并不改变武器能力。

候选答案：No. A Planetary Fortress can attack ground targets only.

**C 的理由：** 行星要塞不能对空这一结论正确；末尾所谓澄清目标层级为包括空中并不会改变武器对地限制，容易暗示澄清即可允许对空。

候选答案：No. A Planetary Fortress can attack only ground targets.

## 3/100 sc2qa_000385

原标签：`ambiguous`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** Can the Roach attack an airborne target?

**原参考答案：** The Roach's attack capabilities are restricted to ground targets, as indicated by its weapon specifications. Both the unit's general targeting attributes and its primary weapon explicitly list only ground as a valid target layer. Therefore, it cannot engage aerial units unless a specific condition clarifies otherwise.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | complete | single_hop | high |
| B | 部分正确 | 有效 | not_applicable | single_hop | high |
| C | 部分正确 | 有效 | not_applicable | single_hop | high |

**A 的理由：** 蟑螂不能攻击空中目标的主体结论正确，但所谓存在特定条件即可澄清为可攻击没有具体机制支撑；对已明确空中的目标无需再问层。

候选答案：No. Roaches can attack only ground targets.

**B 的理由：** 蟑螂普通攻击不能对空，前段正确；‘unless a specific condition clarifies otherwise’没有说明任何真实机制，制造了不存在的泛化例外。

候选答案：No. A Roach's normal attack targets ground units only.

**C 的理由：** 蟑螂没有对空攻击；答案附加的某种条件可澄清例外未提供具体机制，削弱了明确的否定结论。

候选答案：No. Roaches attack ground targets only.

## 4/100 sc2qa_000406

原标签：`single_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** What is the production time of a Widow Mine?

**原参考答案：** The Widow Mine has a production time of 30.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | uncertain | single_hop | medium |
| B | 部分正确 | 有效 | missing | single_hop | medium |
| C | 无法核实 | 有效 | uncertain | single_hop | medium |

**A 的理由：** 仅给出30没有秒或游戏速度口径；寡妇雷生产计时可能是以普通速度数据计量，不能据此断言数值错误，但答案不自足。

未解决项：30的计时口径未给出，尚未外部核实。

候选答案：Specify the time unit and game-speed convention for the Widow Mine production time.

**B 的理由：** 生产时间写成裸数30，没有秒或游戏时间口径，无法形成可复用的完整数值答案；不据此审计版本。

未解决项：30采用的计时单位和游戏速度口径未提供。

**C 的理由：** 给出30但没有时间单位或游戏时间/现实时间口径，无法直接认定生产时间这个数值。应明确采用的计时口径后核实。

未解决项：30可能是数据中的游戏秒数；目前无原始数据或时间口径。

## 5/100 sc2qa_000268

原标签：`two_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** How much mineral and gas does it cost to summon a Nydus Worm from a Nydus Network, and what is the survival armor value of the Nydus Network itself?

**原参考答案：** Summoning a Nydus Worm costs 75 minerals and 75 gas. The Nydus Network structure has a survival armor value of 1.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 回答分别对应虫洞虫召唤的75矿75气和虫洞网络本体1护甲；这是两个并列直接属性，不构成相互依赖的两步推理。

候选答案：A Nydus Worm costs 75 minerals and 75 gas; the Nydus Network has 1 base armor.

**B 的理由：** 答案区分坑道网络召唤坑道虫的75矿75气费用与网络本体1点护甲，没有把网络建造费用或虫的护甲混在一起。两个并列属性不构成两步依赖。

候选答案：Summoning a Nydus Worm costs 75 minerals and 75 gas; the Nydus Network has 1 base armor.

**C 的理由：** 坑道虫召唤费用75矿75气与坑道网络基础护甲1符合所知机制；两项是并列属性查询，不需把一个属性推导为另一个。

候选答案：A Nydus Worm costs 75 minerals and 75 vespene gas; a Nydus Network has 1 base armor.

## 6/100 sc2qa_000349

原标签：`multi_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** What is the sequence of buildings required to construct a Dark Templar?

**原参考答案：** To construct a Dark Templar, you must first build a Twilight Council. The Twilight Council itself requires a Cybernetics Core as a prerequisite. Therefore, the Cybernetics Core is the foundational building needed to unlock the Dark Templar.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 有效 | missing | multi_hop | high |
| C | 存在错误 | 有效 | missing | multi_hop | high |

**A 的理由：** 黑暗圣堂武士直接要求黑暗圣坛，并从传送门或折跃门生产；答案停在暮光议会和控制芯核，漏掉关键黑暗圣坛，也未给出完整建筑链。

候选答案：Build a Pylon and Gateway, then a Cybernetics Core, Twilight Council, and Dark Shrine. Train the Dark Templar at a Gateway or warp it in from a Warp Gate.

**B 的理由：** 黑暗圣堂武士还必须由黑暗圣坛解锁；仅列暮光议会和控制核心不能生产。完整科技关系包含网关、控制核心、暮光议会、黑暗圣坛，最后在网关或折跃门生产。

候选答案：Build a Gateway, Cybernetics Core, Twilight Council, and Dark Shrine; then train a Dark Templar at a Gateway or warp one in through a Warp Gate.

**C 的理由：** 黑暗圣堂武士需要黑暗圣坛；答案遗漏这一直接科技要求，也未提到兵营/折跃门生产，错误地把暮光议会当作足够的末端条件。

候选答案：Build a Gateway, Cybernetics Core, Twilight Council, and Dark Shrine. Then train a Dark Templar at a Gateway or warp one in through a Warp Gate, with the usual power requirements.

**玩家补充核查：** 黑暗圣堂的前置链缺少黑暗圣坛，给出的祖先链不能充分解锁该单位。 TRAIN_INFO 的 GATEWAY→DARKTEMPLAR 项要求 DARKSHRINE；官方黑暗圣堂进攻指南也包括黑暗圣坛。 外部来源支持此项问题；建议答案仍需纳入全数据修订流程。

来源：[S1](https://raw.githubusercontent.com/BurnySc2/python-sc2/develop/sc2/dicts/unit_train_build_abilities.py)；[S2](https://news.blizzard.com/en-us/article/5963107/game-guide-protoss-attacks)

关系修正候选：Dark Templar production requires a Dark Shrine. The technology path includes Gateway, Cybernetics Core, Twilight Council, and Dark Shrine; the unit is then trained at a Gateway or warped in through an available Warp Gate.

## 7/100 sc2qa_000989

原标签：`ambiguous`；生成模型：`zai-org/GLM-5.2`。

**问题：** Can a Siege Tank attack an enemy unit that approaches its position?

**原参考答案：** The Siege Tank's weapon can only target ground units, dealing 40 damage with a range of 13 and a cooldown of 3, plus 30 bonus damage against armored targets. Since its target layer is restricted to ground, whether it can attack the approaching enemy depends on whether that enemy is a ground unit or an air unit. If the enemy is airborne, the Siege Tank cannot attack it.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 需澄清 | missing | ambiguous | high |
| B | 部分正确 | 需澄清 | missing | ambiguous | high |
| C | 部分正确 | 需澄清 | missing | ambiguous | high |

**A 的理由：** 是否能攻击不仅取决于对地：题干没有说明坦克模式、距离或视野；射程13及慢射速属于攻城模式，且有最小射程。答案把模式专属武器当成通用武器。

未解决项：答案中的40、30及冷却3未外部核查，不能据这些数字单独判错。

候选答案：It can attack a visible ground enemy within the weapon range of its current mode. In siege mode it also has a minimum range; it cannot attack air units.

**B 的理由：** 答案给出的是架起模式的射程和伤害，却没有说明模式；架起坦克还存在最小射程，敌人接近并非只需区分地面与空中。目标距离、模式、可见性会影响是否能打。

未解决项：具体伤害和冷却没有提供武器模式及计时口径，不据此认定数值错误。

候选答案：A Siege Tank can attack a visible ground target in its weapon range. In Siege Mode it cannot fire inside its minimum range; it cannot attack air units.

**C 的理由：** 射程13和40加30对重甲描述的是攻城模式。题目未说明模式、距离或目标层级；即使是地面目标，进入攻城炮最小射程内也不能直接攻击，答案只保留对地条件不够。

候选答案：It depends on the target's layer, the tank's mode, and distance. Both modes attack ground targets; siege mode also has a minimum firing range.

## 8/100 sc2qa_000819

原标签：`single_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** How much damage does the Photon Cannon deal with its weapon?

**原参考答案：** The Photon Cannon deals 20 damage with its weapon.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 光子炮一次命中基础伤害20，直接回答武器伤害问题，无需额外生产或科技条件。

候选答案：A Photon Cannon deals 20 base damage per hit.

**B 的理由：** 光子炮基础单次武器伤害20，答案直接给出所问属性；未把对目标护甲结算后的伤害与基础伤害混淆。

候选答案：A Photon Cannon deals 20 base damage per shot.

**C 的理由：** 光子炮基础单次伤害20，直接回答武器伤害；题目未要求对特定护甲目标的实际扣血。

候选答案：A Photon Cannon deals 20 base damage per attack.

## 9/100 sc2qa_000843

原标签：`single_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** What is the movement speed of the Mothership Core?

**原参考答案：** The Mothership Core has a movement speed of 1.88.

**汇总分流：** 两方未发现答案实质问题，另一方有不同意见。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 无法核实 | 有效 | uncertain | single_hop | low |
| C | 未发现实质问题 | 有效 | complete | single_hop | medium |

**A 的理由：** 1.88可对应母舰核心常用基础数据口径的移动速度；题目为直接属性询问，未发现机制性错误。

未解决项：未外部核查数据的速度口径。

候选答案：The Mothership Core has a base movement speed of about 1.88 in the stated data convention.

**B 的理由：** 1.88属于母舰核心移动速度的具体数值；输入没有单位或速度口径，当前仅凭机制记忆不能充分确认该数字，不以版本差异判错。

未解决项：需要对应的速度单位或原始数据才能核定1.88。

**C 的理由：** 母舰核心移动速度约1.88是熟知的数据口径；问题为直接数值属性查询，未发现实质错误，不因该单位是否仍可用而审计版本。

未解决项：未提供原始数据标尺；此判断基于所知单位数值。

候选答案：The Mothership Core's movement speed is approximately 1.88 in the stated game-data speed scale.

## 10/100 sc2qa_000356

原标签：`ambiguous`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** Can the Colossus attack an enemy target when its ground-or-air layer is not specified?

**原参考答案：** The Colossus can attack enemies, but its ability is restricted to ground targets only. Both its general targeting attributes and its primary weapon specify that they target ground units. Therefore, it cannot attack air units, and the target's layer must be clarified as ground for the attack to be valid.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 需澄清 | complete | ambiguous | high |
| B | 未发现实质问题 | 需澄清 | complete | ambiguous | high |
| C | 未发现实质问题 | 需澄清 | complete | ambiguous | high |

**A 的理由：** 巨像的武器只对地，目标层缺失导致能否攻击无定论；答案没有把巨像自身可被对空武器命中的特性混入攻击目标范围。

候选答案：A Colossus can attack ground targets only; clarify whether the target is ground or air.

**B 的理由：** 巨像普通武器只能攻击地面；目标层缺失时答案正确给出条件限制。巨像本体可受对空攻击不代表其武器可对空。

候选答案：A Colossus can attack ground targets only; the target's layer must be known to decide whether it can engage.

**C 的理由：** 巨像武器只能对地，答案针对未给目标层级正确作条件判断。巨像本身可被对空攻击不等于其武器能对空，答案没有混淆这两种关系。

候选答案：A Colossus can attack only ground targets; the target's layer must be known to decide.

## 11/100 sc2qa_000758

原标签：`ambiguous`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** Can the Reaper attack an enemy unit if I don't know whether it's a ground or air target?

**原参考答案：** The Reaper can only attack ground units. The weapon data explicitly specifies ground as the target type, with no indication of air capability. To determine if an attack is possible, you would need to clarify whether the target is a ground unit.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 需澄清 | complete | ambiguous | high |
| B | 未发现实质问题 | 需澄清 | complete | ambiguous | high |
| C | 未发现实质问题 | 需澄清 | complete | ambiguous | high |

**A 的理由：** 死神普攻仅对地；题干故意缺少目标层，答案准确给出需先确认地面目标这一条件。

候选答案：A Reaper can attack only ground units, so the target layer must be clarified.

**B 的理由：** 死神手枪只能对地；不知道目标层便不能确定普通攻击是否可用，答案的条件判断成立。

候选答案：A Reaper can attack ground targets, but cannot attack air targets.

**C 的理由：** 死神常规武器只能对地；答案准确指出目标层级缺失使具体攻击判断无法确定，没有把缺信息误作更深推理。

候选答案：A Reaper can attack only ground targets, so the target must be identified as ground.

## 12/100 sc2qa_000178

原标签：`ambiguous`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** What does the High Templar need to use Psionic Storm?

**原参考答案：** The High Templar requires at least 75 energy to cast Psionic Storm, and the ability has a cooldown of 1.43 seconds. Additionally, Psionic Storm must be researched from the Templar Archives before it can be used. The ability can target both air and ground units within a range of 9.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | two_hop | medium |

**A 的理由：** 心灵风暴需圣堂文库研究和75能量，施法范围9、能同时伤及地面与空中；答案覆盖主要激活门槛。

未解决项：1.43秒冷却未逐项外部核实，但未发现实质矛盾。

候选答案：Research Psionic Storm at the Templar Archives and have at least 75 energy on the High Templar.

**B 的理由：** 75能量与圣堂文献馆研究心灵风暴是必要解锁条件，9射程和对空对地区域效果也符合该技能机制。列出多个直接条件不自动成为多跳。

未解决项：1.43秒采用的游戏计时口径未单独说明，但不影响主要条件判断。

候选答案：Psionic Storm must be researched at the Templar Archives, and the High Templar needs at least 75 energy and a valid target point within range.

**C 的理由：** 施放风暴需圣堂文库研究与75能量，均已说明；范围9及可伤害空地单位符合该技能机制，额外冷却值未发现明确矛盾。

未解决项：冷却1.43秒未获得原始数据验证。

候选答案：Psionic Storm must be researched at the Templar Archives, and a High Templar needs at least 75 energy to cast it.

## 13/100 sc2qa_000328

原标签：`multi_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** What is the production prerequisite chain for the Oracle unit?

**原参考答案：** The Oracle is a Protoss unit that is produced from a Stargate. To build a Stargate, a Gateway is required as a prerequisite building. Therefore, the production route involves using a Gateway to unlock the Stargate, which then produces the Oracle.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 有效 | missing | multi_hop | high |
| C | 存在错误 | 有效 | missing | multi_hop | high |

**A 的理由：** 星门的直接前置是控制芯核，不能由传送门直接解锁。答案省掉控制芯核，导致所述先后链不能实际生产先知。

候选答案：Build a Gateway, then a Cybernetics Core, then a Stargate; produce the Oracle at the Stargate. Powered Protoss structures also require Pylon power.

**B 的理由：** 星门的直接科技前置是控制核心，不是网关。正确顺序须经网关到控制核心再到星门，答案跳过了必需的一环。

候选答案：Build a Gateway, then a Cybernetics Core, then a Stargate; the Stargate produces Oracles.

**C 的理由：** 先知由星门生产正确，但星门直接前置是控制核心；仅有兵营不足以建星门，所谓完整生产链跳过了控制核心。

候选答案：Build a Gateway, then a Cybernetics Core, then a Stargate; train the Oracle at the Stargate.

**玩家补充核查：** 星门的直接前置被写成传送门（Gateway），省略控制核心。 PROBE→STARGATE 的 required_building 为 CYBERNETICSCORE。 外部来源支持关键前置遗漏。

来源：[S1](https://raw.githubusercontent.com/BurnySc2/python-sc2/develop/sc2/dicts/unit_train_build_abilities.py)

关系修正候选：An Oracle is produced at a Stargate. The path includes Gateway, Cybernetics Core, and Stargate; the Cybernetics Core is the Stargate's direct technology prerequisite.

## 14/100 sc2qa_000408

原标签：`single_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** What is the movement speed of a flying Locust?

**原参考答案：** A flying Locust has a movement speed of 2.62.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | medium |

**A 的理由：** 飞行蝗虫的2.62是可识别的基础速度数据表达；未把降落后的地面移动或攻击能力混淆进来。

未解决项：没有外部核实速度计量口径。

候选答案：A flying Locust has a base movement speed of about 2.62 in the data convention used here.

**B 的理由：** 2.62与飞行蝗虫通常列出的基础移动速度相符，答案针对飞行形态，没有误用落地蝗虫的移动速度。

未解决项：实际秒数换算取决于游戏速度口径，输入未说明。

候选答案：A flying Locust has a base movement speed of approximately 2.62 game units per game second.

**C 的理由：** 飞行蝗虫移动速度2.62与常见原始游戏速度标尺相符；答案是直接属性查询，没有把落地蝗虫速度混入。

未解决项：未提供速度标尺原始证据。

候选答案：A flying Locust has a movement speed of about 2.62 in the game-data speed scale.

## 15/100 sc2qa_000713

原标签：`multi_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** What are the resource costs to produce a Protoss Observer, and what building must be built first to unlock the Robotics Facility that produces it?

**原参考答案：** A Protoss Observer costs 25 minerals and 75 gas and requires 1 supply. The Observer is produced from a Robotics Facility. However, before a Robotics Facility can be constructed, a Gateway must be built first, since the Robotics Facility requires a Gateway as its prerequisite building.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | two_hop | high |
| B | 存在错误 | 有效 | missing | two_hop | high |
| C | 部分正确 | 有效 | missing | multi_hop | high |

**A 的理由：** 观察者25矿75气1人口及机械台生产正确，但机械台直接需要控制芯核而非传送门；传送门是更早的间接前置。

候选答案：An Observer costs 25 minerals and 75 gas and uses 1 supply. Build a Cybernetics Core to unlock the Robotics Facility; the Cybernetics Core itself requires a Gateway.

**B 的理由：** 侦察器25矿75气1人口正确；机械台的直接前置为控制核心，网关只是更早的间接前置，答案将其说成机械台唯一直接前置会漏建控制核心。

候选答案：An Observer costs 25 minerals and 75 gas and uses 1 supply. A Cybernetics Core is required before building its Robotics Facility; the Core in turn requires a Gateway.

**C 的理由：** 侦察器25矿75气和1人口正确，机械台生产也正确；机械台的直接科技前置是控制核心，答案把较早的兵营写成直接前置。

候选答案：An Observer costs 25 minerals and 75 gas and uses 1 supply. A Robotics Facility produces it and requires a Cybernetics Core, which in turn requires a Gateway.

**玩家补充核查：** 观察者题把机械台的直接前置写成传送门（Gateway），缺控制核心。 PROBE→ROBOTICSFACILITY 的 required_building 为 CYBERNETICSCORE。 只核查科技关系，不代表本题全部资源数值已核验。

来源：[S1](https://raw.githubusercontent.com/BurnySc2/python-sc2/develop/sc2/dicts/unit_train_build_abilities.py)

关系修正候选：An Observer is produced at a Robotics Facility, whose direct technology prerequisite is a Cybernetics Core. The path also includes a Gateway before the Cybernetics Core.

## 16/100 sc2qa_000110

原标签：`multi_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** To build a Starport Tech Lab using a Factory, which building must be constructed first?

**原参考答案：** The Starport Tech Lab can be produced from a Factory. However, a Factory requires a Barracks to be built before it. The Barracks is a Terran building.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 需澄清 | missing | ambiguous | high |
| B | 存在错误 | 无效 | missing | ambiguous | high |
| C | 部分正确 | 需澄清 | missing | ambiguous | high |

**A 的理由：** 工厂前置兵营这一点正确，但工厂建造的是可共用的科技实验室；需要星港飞起换挂才能成为星港所用实验室。题目把附件归属与建造来源混为一谈。

候选答案：Build a Barracks before a Factory. A Factory may build a Tech Lab, then lift off so a Starport can land beside and use that add-on.

**B 的理由：** 工厂可以建自己的科技实验室，之后可通过起飞换挂让星港接入；不能直接把‘星港科技实验室由工厂生产’当成常规建造关系。兵营先于工厂属实，但没有纠正错误前提。

候选答案：A Barracks is required before a Factory. A Factory can build a Tech Lab that a Starport can later use after an add-on swap; a Starport can also build its own Tech Lab.

**C 的理由：** 兵工厂需兵营这个前置正确；但兵工厂建的是自己的科技实验室，星港要使用需起飞并落到兼容附属建筑旁。题干的用兵工厂建星港实验室需要解释交换附属建筑这一语义。

候选答案：A Barracks must be built before a Factory. The Factory can build a Tech Lab that a Starport can later use by lifting off and landing beside it.

## 17/100 sc2qa_000952

原标签：`ambiguous`；生成模型：`zai-org/GLM-5.2`。

**问题：** Are there any specific conditions required for a Queen to activate her Transfusion ability?

**原参考答案：** Although Transfusion is considered always available, it can only be activated while the Queen is on creep. The ability also requires 50 energy per cast and has a 1 second cooldown. Since the Queen has a maximum energy pool of 200, she can cast it multiple times as long as she has the energy and remains on creep.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | single_hop | medium |
| B | 部分正确 | 有效 | missing | single_hop | high |
| C | 部分正确 | 有效 | missing | two_hop | medium |

**A 的理由：** 50能量、女王自身在菌毯上是关键条件；但是仍需处于施法距离内的合法生物友方目标，并非只要女王有能量和菌毯就能随意施放。

未解决项：1秒冷却的时间口径未外部核实。

候选答案：Transfusion requires 50 energy, the Queen to be on creep, and a valid friendly biological target within cast range.

**B 的理由：** 菌毯和50能量是重要条件，但输血还需要有效的友方生物目标及施法距离。‘有能量且站菌毯即可多次施放’漏掉目标合法性；200能量上限不能代替该条件。

未解决项：1秒冷却的计时口径未核验。

候选答案：A Queen needs 50 energy, must be on creep, and needs a valid friendly biological target within Transfusion range; the ability must also be ready.

**C 的理由：** 女王在菌毯上且有50能量是核心施法条件；还应有射程内可被输血的友方生物目标且目标需要治疗。1秒冷却的时间口径未说明，不能据此断言精确冷却。

未解决项：1秒冷却与真实计时之间的口径未核实。

候选答案：The Queen needs 50 energy, must be on creep, and needs an eligible injured biological target in cast range.

## 18/100 sc2qa_000061

原标签：`two_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** How does the Viper's Consume ability interact with its shield?

**原参考答案：** The Viper has no shield, so its shield value is 0. Consume deals 150 damage to a friendly building over 14 seconds and grants 50 energy, but it does not affect the shield.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | not_applicable | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | medium |
| C | 未发现实质问题 | 需澄清 | not_applicable | single_hop | high |

**A 的理由：** 飞蛇没有护盾，吞噬是消耗友方建筑生命来补充能量，不能恢复自身护盾。官方资料明确有150点消耗量；未发现答案主要机制错误。

未解决项：官方页面只直接支持150点伤害，14秒与50能量依赖机制知识。

候选答案：Consume does not interact with the Viper’s shields: Vipers have none. It drains a friendly structure’s life to restore energy.

查阅来源：[1](https://news.blizzard.com/en-us/article/24009150/starcraft-ii-5-0-12-patch-notes)

**B 的理由：** 飞蛇自身没有护盾；吞噬从友方建筑汲取生命换能量，不会给飞蛇生成或消耗护盾。所问护盾关系回答清楚，附加150伤害与50能量符合常见数据。

未解决项：吞噬持续时间的具体计时口径未外查。

候选答案：A Viper has no shields. Consume damages a friendly structure to restore the Viper's energy and does not alter the Viper's shields.

**C 的理由：** 飞蛇无护盾，答案正确澄清此前提；吞噬转化友方建筑生命为自身能量，不影响自身护盾。额外150建筑伤害已由实际访问的暴雪官方说明支持。

候选答案：Vipers have no shields. Consume drains health from an eligible friendly structure to restore the Viper's energy; it does not restore shields.

查阅来源：[1](https://news.blizzard.com/en-us/article/24009150/starcraft-ii-5-0-12-patch-notes)

## 19/100 sc2qa_000566

原标签：`ambiguous`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** What prevents a Stalker from using Blink freely?

**原参考答案：** A Stalker cannot use Blink freely due to explicit activation restrictions. The ability is only available after the Blink upgrade is researched at the Twilight Council. After it is unlocked, Blink has a 7-second cooldown that restricts how frequently it can be cast. Additionally, the Stalker can only teleport to a target location within a range of 8, limiting where the ability can be used.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | single_hop | high |
| B | 部分正确 | 有效 | missing | single_hop | high |
| C | 部分正确 | 有效 | missing | two_hop | high |

**A 的理由：** 闪烁研究、冷却和距离限制描述合理，但能否落点还要求可通行且有视野；若问不能自由闪烁的限制，漏掉视野尤其会误导跨高地操作。

未解决项：7秒冷却未外部核实计时口径。

候选答案：Blink requires its Twilight Council research, a ready cooldown, and a visible, pathable destination within range 8.

**B 的理由：** 闪烁研究、冷却和8距离限制正确，但还必须能看见合法目的地，不能仅因在8范围内就随意跨越到黑雾位置。题问不能自由使用的限制，应补充视野。

候选答案：Blink requires research at the Twilight Council, has a cooldown, and can move a Stalker only to a valid visible location within range 8.

**C 的理由：** 研究、冷却和距离限制均相关，但追猎闪烁落点还受视野和可通行地形限制；任意范围8以内的位置并非都可瞬移。

候选答案：Blink requires research, an available cooldown, and a valid visible destination within its range. Terrain and destination visibility also restrict its use.

**玩家补充核查：** 闪烁可用条件遗漏目标位置的视野要求。 官方 Blink Stalker Rush 部分说明闪烁到高地需要目标高地视野。 外部来源支持视野条件；不判定已列条件必然全部错误。

来源：[S2](https://news.blizzard.com/en-us/article/5963107/game-guide-protoss-attacks)

关系修正候选：Blink requires the Blink upgrade, readiness after its cooldown, and a valid destination within range with the required vision and terrain conditions.

## 20/100 sc2qa_000665

原标签：`two_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** What is the energy cost of the Microbial Shroud ability and what is the mineral cost to produce an Infestor?

**原参考答案：** The Microbial Shroud ability costs 75 energy to activate. An Infestor costs 100 minerals, 150 gas, and 2 supply to produce from larva, with a production time of 36 seconds.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | medium |

**A 的理由：** 75能量与100矿回答了两个独立属性问题；额外150气、2人口和幼虫生产与常见数据一致。36秒是附加计时，非核心回答。

未解决项：不作版本审计；附加36秒生产时间的速度口径未逐项核实。

候选答案：Microbial Shroud costs 75 energy, and an Infestor costs 100 minerals (plus 150 gas).

**B 的理由：** 微生物菌毯75能量、感染虫100矿回答了两个并列的直接成本；额外列150气与2人口没有改变结论。

未解决项：额外的36秒生产时间未给出计时口径，主问题不依赖该数值。

候选答案：Microbial Shroud costs 75 energy, and an Infestor costs 100 minerals.

**C 的理由：** 微生物遮蔽75能量、感染虫100矿150气2人口符合所知数据；两项所问成本是并列查询，额外生产时间不构成必要推理。

未解决项：36秒生产时间属于额外说明，其计时口径未给出。

候选答案：Microbial Shroud costs 75 energy, and an Infestor costs 100 minerals.

## 21/100 sc2qa_000603

原标签：`single_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** How long does it take to produce a Photon Cannon?

**原参考答案：** A Photon Cannon requires 40 seconds to construct.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | medium |

**A 的理由：** 光子炮40秒是常见基础建造时间口径；答案包含单位，直接回应建造时长，没有涉及错误的生产建筑。

未解决项：游戏速度换算未指定，未据此判错。

候选答案：A Photon Cannon takes 40 seconds to construct in the base-time convention.

**B 的理由：** 40秒是光子炮常见的基础建造时间表述；题目问建造时长，答案给出单位且未把探机持续施工当作必要条件。

未解决项：游戏速度换算口径未提供。

候选答案：A Photon Cannon takes 40 game seconds to build in the stated time scale.

**C 的理由：** 光子炮40秒建造时间符合常用游戏数据时间口径；题目直接询问建造时长，没有把生产单位和建造建筑误作不同过程。

未解决项：未说明游戏速度，因此实际墙钟秒数不能从此直接得出。

候选答案：A Photon Cannon takes 40 game-time seconds to build in the stated data timing scale.

## 22/100 sc2qa_000013

原标签：`single_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** What is the armor value of the Greater Spire?

**原参考答案：** The Greater Spire has an armor value of 1.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 大龙塔基础护甲1，问题没有指向升级后的护甲，按基础属性回答成立。

候选答案：A Greater Spire has 1 base armor.

**B 的理由：** 大龙塔本体基础护甲为1；答案直接回应护甲属性，没有把生命值或升级费用混入。

候选答案：A Greater Spire has 1 base armor.

**C 的理由：** 大龙塔基础护甲为1，与答案一致；未发现将护甲与生命值或升级等级混淆。

候选答案：The Greater Spire has 1 base armor.

## 23/100 sc2qa_000164

原标签：`ambiguous`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** What condition must be met for the Baneling to use its Disable Attack Building ability?

**原参考答案：** The ability activates when the Baneling has a structure targeted or when a structure is within its range. No other conditions are required for its activation.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | single_hop | high |
| B | 存在错误 | 需澄清 | missing | ambiguous | high |
| C | 存在错误 | 需澄清 | uncertain | ambiguous | medium |

**A 的理由：** Disable Attack Building 是禁止自动攻击建筑的切换命令，不是建筑进入范围时才触发的攻击技能；答案把目标过滤开关误作目标条件触发。

候选答案：Disable Attack Building is a toggle that prevents the Baneling from automatically attacking structures; a structure does not need to be targeted or in range to toggle it.

**B 的理由：** Disable Attack Building是爆虫攻击建筑行为的切换命令，不是靠‘选中建筑或建筑进入射程’触发的主动伤害技能。答案把开关状态与攻击目标条件混淆。

未解决项：原始数据中的技能名称及默认开关状态未提供。

候选答案：Disable Attack Building toggles off a Baneling's automatic attacks against structures; it does not require a structure to be targeted or nearby.

**C 的理由：** 禁用攻击建筑是爆虫攻击建筑行为的切换命令，不能由建筑被选中或进入射程推导其激活条件；答案把攻击目标条件误作切换能力的前置。

未解决项：应核实该命令在原始数据中的启用/禁用状态条件。

候选答案：Disable Attack Building toggles whether a Baneling automatically attacks structures. Selecting or approaching a structure is not the activation requirement for this toggle.

## 24/100 sc2qa_000527

原标签：`multi_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** What Zerg building is the tech prerequisite for the structure that produces the Ultralisk Cavern?

**原参考答案：** The Ultralisk Cavern is produced from a Spire and costs 150 minerals and 200 gas. The Spire requires a Lair as a tech prerequisite building. The Lair is a Zerg building in this prerequisite chain.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 无效 | missing | ambiguous | high |
| B | 存在错误 | 无效 | missing | ambiguous | high |
| C | 存在错误 | 无效 | missing | ambiguous | high |

**A 的理由：** 雷兽窟由工蜂建造、科技要求蜂巢，不由飞龙塔生产。题目所指生产它的建筑这一关系本身错误，答案以飞龙塔和虫穴继续构造了错误链。

候选答案：An Ultralisk Cavern is built by a Drone and requires a Hive. It is not produced by a Spire.

**B 的理由：** 雷兽窟由工蜂变形建造，科技要求为蜂巢，并非由飞龙塔生产；答案整条飞龙塔—主巢推论建立在错误生产关系上。

候选答案：An Ultralisk Cavern is built by a Drone and requires a Hive. A Spire does not produce it.

**C 的理由：** 雷兽窟不是由飞龙塔生产，而由工蜂建造并要求主巢科技。答案整条飞龙塔—虫穴—雷兽窟链不存在；题目也应澄清所谓生产该建筑的结构。

候选答案：A Drone builds an Ultralisk Cavern, and a Hive is its direct technology prerequisite. A Spire is not part of this requirement.

**玩家补充核查：** 把雷兽窟写成由飞龙塔生产，并给出错误科技路径。 DRONE→ULTRALISKCAVERN 的 required_building 为 HIVE。 外部来源支持关系错误；未核验题中所有数值。

来源：[S1](https://raw.githubusercontent.com/BurnySc2/python-sc2/develop/sc2/dicts/unit_train_build_abilities.py)

关系修正候选：An Ultralisk Cavern is constructed by a Drone and requires a Hive. It is not produced by a Spire.

## 25/100 sc2qa_000746

原标签：`multi_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** What building prerequisites must be satisfied to unlock the Lurker Burrowed unit?

**原参考答案：** To access the Lurker Burrowed, a Lurker Den must be built first. The Lurker Den itself requires a Hydralisk Den to be constructed. The Hydralisk Den is the base building that provides the prerequisite for the Lurker Den.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 需澄清 | missing | multi_hop | high |
| B | 部分正确 | 需澄清 | missing | two_hop | high |
| C | 部分正确 | 需澄清 | missing | multi_hop | high |

**A 的理由：** 刺蛇塔→潜伏者巢的科技方向基本正确，但漏虫穴等级前置；潜地潜伏者是潜伏者潜地后的状态，还需刺蛇变异潜伏者并执行潜地，不能把它当独立建筑解锁生产。

候选答案：Reach Lair tech, build a Hydralisk Den and Lurker Den, morph a Hydralisk into a Lurker, and burrow the Lurker.

**B 的理由：** 地刺穴需要刺蛇巢这一关系正确，但完整建筑要求还含主巢科技；潜地地刺是地刺的状态，要先有刺蛇并变地刺再潜地，不能把状态当独立建筑产物。

候选答案：Reach Lair tech and build a Hydralisk Den, then a Lurker Den. Morph a Hydralisk into a Lurker and burrow it to obtain the burrowed form.

**C 的理由：** 潜伏者巢穴与刺蛇巢关系正确，但巢穴还需虫穴等级科技；Burrowed是潜伏者的钻地状态，并非单独建筑生产的单位。应区分解锁潜伏者与进入钻地形态。

候选答案：A Lurker Den requires a Hydralisk Den and Lair-level technology. Morph a Hydralisk into a Lurker, then use its burrow command to enter the burrowed form.

## 26/100 sc2qa_000236

原标签：`single_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** What is the gas cost required to produce a Protoss Stargate?

**原参考答案：** The Protoss Stargate has a production cost of 150 Vespene Gas.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 星门的气矿消耗150，回答只报所问资源，不混淆150矿的另一半费用。

候选答案：A Stargate costs 150 Vespene gas.

**B 的理由：** 星门建造费用包含150气，答案只给题目要求的气矿成本，没有误写为星门单位的费用。

候选答案：A Stargate costs 150 vespene gas.

**C 的理由：** 星门气体造价150，直接回答所问的单个资源属性，无需完整重复矿物造价。

候选答案：A Stargate costs 150 vespene gas.

## 27/100 sc2qa_000965

原标签：`ambiguous`；生成模型：`zai-org/GLM-5.2`。

**问题：** Can a Sentry cast Guardian Shield freely at any time, or are there conditions that must be met first?

**原参考答案：** Guardian Shield is described as always available, but its ability text also lists explicit activation constraints. The ability costs 75 energy and has a cooldown of 12.86 seconds, so a Sentry must have at least 75 energy and must not be on cooldown to cast it. Since a Sentry can store up to 200 energy, it can cast Guardian Shield more than once if enough energy has been banked, but each cast still respects the cooldown timer.

**汇总分流：** 两方未发现答案实质问题，另一方有不同意见。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 无法核实 | 有效 | uncertain | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | two_hop | medium |

**A 的理由：** 守护者之盾需要75能量且不能在自身冷却中重复施放；无需另行研究。最大200能量只是解释储能可支持多次施放，并未声称绕过冷却。

未解决项：12.86秒冷却的精确取值尚未以原始游戏数据核实。

候选答案：Guardian Shield requires at least 75 energy and its cooldown to be ready.

**B 的理由：** 守护者之盾需75能量且无需研究这一核心机制成立，但答案将12.86秒明确称为再施法冷却；此处不能仅凭持续时间或能量上限推出冷却，尚无法确认该数值。

未解决项：12.86是否为实际冷却及其时间口径仍待数据核验；未取得可访问外部资料。

候选答案：Guardian Shield is available without research and costs 75 energy; the Sentry must be able to cast abilities.

**C 的理由：** 守护者之盾需75能量，处在技能冷却时不能再次施放；答案明确区分无需研究解锁与无需能量限制。200能量仅作可重复施放的上限背景。

未解决项：12.86秒冷却值未独立外查，但符合常见快速度换算。

候选答案：A Sentry needs at least 75 energy and Guardian Shield must be off cooldown; it does not require research.

## 28/100 sc2qa_000311

原标签：`multi_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** Which Protoss building is the final prerequisite required to construct a Disruptor?

**原参考答案：** To build a Disruptor, a player must first construct a Robotics Facility. The Robotics Facility itself requires a Cybernetics Core as its prerequisite. Therefore, the Cybernetics Core is the foundational building needed to eventually produce a Disruptor.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 有效 | missing | two_hop | high |
| C | 存在错误 | 有效 | missing | two_hop | high |

**A 的理由：** 干扰者的最终科技前置是机械研究所 Robotics Bay；机械台是生产建筑，控制芯核是更早前置，答案没有给出所问的最终建筑。

候选答案：The final tech prerequisite is a Robotics Bay. The Disruptor is produced at a Robotics Facility.

**B 的理由：** 干扰者的最终科技前置是机械研究所；机械台虽为生产建筑，控制核心虽是上游前置，两者都不能替代机械研究所。答案没有回答‘final prerequisite’。

候选答案：A Robotics Bay is the final tech prerequisite for producing a Disruptor at a Robotics Facility.

**C 的理由：** 干扰者由机械台生产，但其最终科技前置是机械研究所；答案改答控制核心，遗漏题目所问的最后解锁建筑。

候选答案：A Robotics Bay is the final technology prerequisite for producing Disruptors at a Robotics Facility.

**玩家补充核查：** 题目问干扰者的最终科技前置，答案只到机械台而遗漏机械研究所。 ROBOTICSFACILITY→DISRUPTOR 项的 required_building 为 ROBOTICSBAY。 外部来源支持遗漏关键前置。

来源：[S1](https://raw.githubusercontent.com/BurnySc2/python-sc2/develop/sc2/dicts/unit_train_build_abilities.py)

关系修正候选：A Disruptor is produced at a Robotics Facility and requires a Robotics Bay. The Robotics Bay is the additional final technology requirement.

## 29/100 sc2qa_000798

原标签：`ambiguous`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** When can an Infestor cast Fungal Growth?

**原参考答案：** Fungal Growth requires 75 energy to activate. An Infestor has a maximum energy pool of 200, so the ability becomes usable once the Infestor has regenerated at least 75 energy. The exact timing depends on energy regeneration and the game state.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | single_hop | high |
| B | 部分正确 | 有效 | missing | single_hop | high |
| C | 部分正确 | 有效 | missing | two_hop | medium |

**A 的理由：** 需拥有75能量正确，但不等于必须新恢复75能量，已有初始能量可计入；还需合法施法位置在范围内。应将存量门槛与恢复量区分。

候选答案：An Infestor can cast Fungal Growth when it has at least 75 energy and can target a legal location within cast range. Existing energy counts toward the 75-energy requirement.

**B 的理由：** 75能量正确，但‘恢复到75即可使用’不足：感染虫需处于可施法状态并选择射程内合法区域；潜地状态不能施放真菌增生。能量上限200与何时可施法不是充分条件。

候选答案：An unburrowed Infestor can cast Fungal Growth when it has at least 75 energy and a valid target point within casting range.

**C 的理由：** 75总能量是关键，但无需重新再生满75：已存在的初始能量也计入。答案未说明感染虫需处于能施法的状态及目标位置在施法范围内，不能把有能量等同于任何时刻可施法。

未解决项：其他特殊状态如禁用效果未在题目中限定。

候选答案：An unburrowed Infestor can cast Fungal Growth when it has at least 75 total energy and a valid target location within casting range.

## 30/100 sc2qa_000003

原标签：`single_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** How much vespene gas does a Starport Tech Lab cost?

**原参考答案：** The Starport Tech Lab costs 25 vespene gas.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 科技实验室造价50矿25气，所问星港科技实验室的气矿25回答正确。

候选答案：A Starport Tech Lab costs 25 Vespene gas.

**B 的理由：** 科技实验室附加建筑气矿费用25，与星港本体100气费用区分清楚。

候选答案：A Starport Tech Lab costs 25 vespene gas.

**C 的理由：** 星港科技实验室需要25气体，答案针对气体造价准确，没有将附属建筑造价与星港造价混淆。

候选答案：A Starport Tech Lab costs 25 vespene gas.

## 31/100 sc2qa_000925

原标签：`multi_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** What building prerequisite chain must a Protoss player complete before they can produce Phoenix?

**原参考答案：** The Phoenix requires a Stargate before it can be produced. The Stargate in turn requires a Gateway as its prerequisite building. The Gateway is a Protoss building, so the full prerequisite chain is Gateway, then Stargate, then Phoenix.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 有效 | missing | multi_hop | high |
| C | 存在错误 | 有效 | missing | multi_hop | high |

**A 的理由：** 凤凰由星门生产正确，但星门直接前置控制芯核，完整链传送门→控制芯核→星门，答案将间接前置误作直接前置。

候选答案：Build a Gateway, then a Cybernetics Core, then a Stargate, which produces Phoenixes. These structures must be powered.

**B 的理由：** 凤凰生产链必须经过控制核心；网关不能直接解锁星门，所谓完整链漏掉必需建筑。

候选答案：Build a Gateway, Cybernetics Core, and Stargate; train Phoenixes at the Stargate.

**C 的理由：** 凤凰由星门生产正确，但所谓完整链漏了星门直接前置控制核心。兵营不能直接解锁星门。

候选答案：Gateway → Cybernetics Core → Stargate → Phoenix, with powered Protoss production structures.

## 32/100 sc2qa_000224

原标签：`single_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** How long does it take to produce a Terran Orbital Command?

**原参考答案：** The production time for a Terran Orbital Command is 25 seconds. This duration is a fixed attribute of the unit's construction process.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | medium |

**A 的理由：** 轨道指挥部25秒对应常见加速游戏计时；它是指挥中心升级而非从兵营生产，答案虽称construction但未给错误来源。

未解决项：答案没有指定游戏速度，fixed一词不应理解为所有速度下真实秒数恒定。

候选答案：Upgrading a Command Center to an Orbital Command takes 25 seconds under the usual faster-speed timing convention.

**B 的理由：** 25秒与轨道指挥部常用升级时长相符；实际为指挥中心升级而非从SCV独立建造，措辞可更准确，但未发现核心数值问题。

未解决项：时间口径未进一步说明。

候选答案：Upgrading a Command Center to an Orbital Command takes 25 seconds in the stated time scale.

**C 的理由：** 轨道指挥部升级需要25游戏时间秒这一数值符合已知数据；更准确表述是指挥中心升级，而非独立建造新的单位。

未解决项：实际墙钟时间受游戏速度口径影响，原题未说明。

候选答案：Upgrading a Command Center to an Orbital Command takes 25 game-time seconds in this timing scale.

## 33/100 sc2qa_000529

原标签：`multi_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** What building must a Zerg player construct before they can build a Roach Warren to unlock Roaches?

**原参考答案：** To unlock the Roach, a player must first construct a Roach Warren. The Roach Warren requires a Spawning Pool as its prerequisite building. Consequently, the Spawning Pool must be built before the Roach Warren in order to produce Roaches.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | two_hop | high |
| B | 未发现实质问题 | 有效 | complete | two_hop | high |
| C | 未发现实质问题 | 有效 | complete | two_hop | high |

**A 的理由：** 蟑螂温室需孵化池；先池后温室解锁蟑螂的两步依赖符合实际。

候选答案：Build a Spawning Pool, then a Roach Warren to unlock Roach production.

**B 的理由：** 蟑螂需要蟑螂温室，温室以前置血池解锁；答案准确回答所问的上游建筑。

候选答案：A Spawning Pool is required before building a Roach Warren, which unlocks Roaches.

**C 的理由：** 血池是蟑螂巢的直接科技前置，蟑螂巢解锁幼虫变蟑螂；答案两步关系明确且正确。

候选答案：A Spawning Pool is required before building a Roach Warren, which unlocks Roach production.

## 34/100 sc2qa_000906

原标签：`multi_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** What is the building prerequisite chain for the Interceptor?

**原参考答案：** The Interceptor requires a Cybernetics Core as a building prerequisite. The Cybernetics Core itself requires a Gateway, which is a Protoss building, before it can be constructed. Consequently, the full building prerequisite chain for the Interceptor goes through the Cybernetics Core back to the Gateway.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 有效 | missing | multi_hop | high |
| C | 存在错误 | 有效 | missing | multi_hop | high |

**A 的理由：** 拦截机由航母生产，控制芯核不是其独立直接建造前置；科技路线还需星门、舰队航标以及航母。答案把航母载机当普通控制芯核单位。

候选答案：The route is Gateway → Cybernetics Core → Stargate → Fleet Beacon → Carrier. Interceptors are then built by the Carrier.

**B 的理由：** 拦截机由航母生产，完整建筑科技链应包括星门和舰队航标；控制核心是间接上游条件，不能被当成拦截机的完整前置。

候选答案：Build a Gateway, Cybernetics Core, Stargate, and Fleet Beacon; produce a Carrier at the Stargate, then build Interceptors from the Carrier.

**C 的理由：** 拦截机由航母在内部制造，控制核心不是其直接生产前置。答案遗漏星门、舰队航标及航母，因而不能称为完整建筑链。

候选答案：Build a Gateway, Cybernetics Core, Stargate, and Fleet Beacon to produce a Carrier at the Stargate. The Carrier then builds Interceptors.

## 35/100 sc2qa_000922

原标签：`multi_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** What building prerequisite chain must Protoss complete to unlock the Archon?

**原参考答案：** The Archon requires a Templar Archives as a building prerequisite. The Templar Archives itself requires a Cybernetics Core before it can be constructed. The Cybernetics Core is a Protoss building, completing the connected prerequisite chain needed to reach the Archon.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 需澄清 | missing | ambiguous | high |
| C | 存在错误 | 有效 | missing | multi_hop | high |

**A 的理由：** 圣堂文库直接需暮光议会，漏暮光议会导致链错误；执政官还可由黑暗圣堂武士合体，不必唯一依赖圣堂文库。

候选答案：Build Gateway → Cybernetics Core → Twilight Council, then Templar Archives for High Templar or Dark Shrine for Dark Templar. Merge two eligible Templar into an Archon.

**B 的理由：** 执政官由两名高阶或黑暗圣堂武士合体，圣堂文献馆不是唯一必要建筑；且文献馆直接前置是暮光议会，不是控制核心。问题须允许文献馆和黑暗圣坛两条路径。

候选答案：After a Gateway, Cybernetics Core, and Twilight Council, build either Templar Archives or a Dark Shrine. Merge any two High Templar and/or Dark Templar into an Archon.

**C 的理由：** 圣堂文库前置还包括暮光议会；执政官来自两名圣堂武士融合，且可用黑暗圣堂路径，不是必须建圣堂文库。答案把一种不完整路径写成唯一必要链。

候选答案：Build a Gateway, Cybernetics Core and Twilight Council, then either Templar Archives for High Templars or a Dark Shrine for Dark Templars. Merge two eligible Templars into an Archon.

## 36/100 sc2qa_000923

原标签：`multi_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** What buildings do I need before I can start producing Disruptors as Protoss?

**原参考答案：** The Disruptor is produced from the Robotics Facility and costs 150 minerals, 150 gas, and 4 supply. The Robotics Facility requires a Gateway as a prerequisite building before it can be constructed. The Gateway is a Protoss building, so you must have a Gateway first, then build a Robotics Facility, and then you can produce Disruptors from it.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 有效 | missing | multi_hop | high |
| C | 存在错误 | 有效 | missing | multi_hop | high |

**A 的理由：** 干扰者150矿150气和机械台生产没问题；但机械台需控制芯核而非仅传送门，且单位还需机械研究所，按答案流程不能生产。

候选答案：Build a Gateway, Cybernetics Core, Robotics Facility, and Robotics Bay. Produce Disruptors at the Robotics Facility for 150 minerals and 150 gas each.

**B 的理由：** 干扰者150矿150气4人口正确，但科技链漏掉控制核心和机械研究所；只有网关加机械台不能开始生产干扰者。

候选答案：Build a Gateway, Cybernetics Core, Robotics Facility, and Robotics Bay; the Robotics Facility then produces Disruptors.

**C 的理由：** 干扰者需要机械研究所，机械台直接前置为控制核心；答案既漏核心又漏研究所，给出的兵营后造机械台即可出干扰者流程不可行。

候选答案：Build a Gateway, Cybernetics Core, Robotics Facility, and Robotics Bay. Produce Disruptors at the Robotics Facility.

## 37/100 sc2qa_000680

原标签：`two_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** What is the Raven's armor value, and how much armor does its Anti-Armor Missile ability reduce?

**原参考答案：** The Raven has a base armor value of 1. Its Anti-Armor Missile ability reduces the armor and shield armor of targeted units by 2 for a duration of 21 seconds.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | medium |

**A 的理由：** 渡鸦基础护甲1，反装甲飞弹削减目标护甲和护盾护甲2，两个直接数值关系回答清楚。

未解决项：附加21秒持续时间未独立核实时间口径。

候选答案：A Raven has 1 base armor. Anti-Armor Missile reduces affected units’ armor and shield armor by 2.

**B 的理由：** 渡鸦基础护甲1，反护甲飞弹使受影响单位护甲与护盾护甲各降低2，答案区分了本体护甲与技能减甲。两个属性无需串联推理。

未解决项：额外21秒持续时间的精确取整与计时口径未外查。

候选答案：A Raven has 1 base armor. Anti-Armor Missile reduces affected units' armor and shield armor by 2.

**C 的理由：** 渡鸦基础护甲1，反装甲导弹减少生命护甲和护盾护甲2，约21秒的表述与所知效果一致。两种属性并列，不需串成多步推理。

未解决项：21为近似时长，未独立核对原始精度。

候选答案：The Raven has 1 base armor. Anti-Armor Missile reduces affected units' armor and shield armor by 2 for about 21 seconds.

## 38/100 sc2qa_000241

原标签：`single_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** What is the base armor value of the Terran Ghost unit?

**原参考答案：** The Terran Ghost has a base armor value of 0. This attribute is a fixed property of the unit's survival statistics.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 幽灵基础护甲0，回答没有与隐形技能、轻甲/重甲标签或升级后的护甲混淆。

候选答案：A Ghost has 0 base armor.

**B 的理由：** 幽灵基础护甲0正确，问题没有要求计算升级后护甲或反护甲效果。

候选答案：A Ghost has 0 base armor.

**C 的理由：** 幽灵基础护甲0正确；额外称其为生存统计固定属性虽赘述，但不影响所问的基础数值。

候选答案：A Ghost has 0 base armor.

## 39/100 sc2qa_000668

原标签：`two_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** What does the Thor's Explosive Payload ability do, and what is the Thor's production cost?

**原参考答案：** Explosive Payload is an always-available ability that arms the Thor's Javelin missile launchers to deal splash damage to nearby air units and additional damage to Light units. The Thor costs 300 minerals, 200 gas, and 6 supply, requires 43 seconds to build, and is produced from the Factory.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 爆裂弹头为雷神对空溅射并对轻甲加伤的模式，与300矿200气6人口费用相符；43秒为额外建造计时，不影响核心回答。

未解决项：附加43秒时间口径未外部核实。

候选答案：Explosive Payload switches the Thor to splash anti-air missiles with bonus damage against Light targets. A Thor costs 300 minerals, 200 gas, and 6 supply.

**B 的理由：** 雷神爆炸载荷模式使用标枪导弹对空溅射并对轻甲加成；300矿200气6人口为正确生产成本。它是模式切换，答案总体表达了切换后的武器效果。

未解决项：附加43秒建造时间的口径未单独核验。

候选答案：Explosive Payload equips the Thor's splash-damage anti-air missiles, which deal bonus damage to Light units. A Thor costs 300 minerals, 200 gas, and 6 supply.

**C 的理由：** 雷神爆炸弹头切换为标枪导弹的对空溅射并对轻甲额外伤害，300矿200气6人口也正确；无需从攻击模式推导成本，属并列查询。

候选答案：Explosive Payload equips the Thor's anti-air splash missiles with bonus damage against Light targets. A Thor costs 300 minerals, 200 gas and 6 supply.

## 40/100 sc2qa_000149

原标签：`multi_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** What is the complete building prerequisite chain for the Swarm Host?

**原参考答案：** The Swarm Host requires an Infestation Pit as a prerequisite building. The Infestation Pit itself requires a Lair. Thus, the Lair must be built first, then the Infestation Pit, and finally the Swarm Host can be constructed.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | multi_hop | high |
| B | 部分正确 | 有效 | missing | multi_hop | high |
| C | 部分正确 | 有效 | missing | multi_hop | high |

**A 的理由：** 虫穴→感染深渊→虫群宿主这段正确，但题目要求complete，虫穴升级还需孵化池，答案缺少这一必要上游建筑。

候选答案：Build a Spawning Pool, upgrade a Hatchery to a Lair, and build an Infestation Pit. Then morph a larva into a Swarm Host.

**B 的理由：** 主巢—感染深渊—虫群宿主的后半链正确，但题目要求完整建筑链，主巢还须由孵化场在有血池条件下升级。答案从主巢直接开始，未交代该前置。

候选答案：Build a Spawning Pool, upgrade a Hatchery to a Lair, and build an Infestation Pit; Swarm Hosts can then be morphed from larvae.

**C 的理由：** 虫群宿主要求感染深渊、感染深渊要求虫穴这一段正确；题目要求完整序列时还应说明孵化场在血池后升级虫穴，以及虫群宿主实际由幼虫变形而非建筑逐个生产。

候选答案：Build a Spawning Pool and upgrade a Hatchery to a Lair, then build an Infestation Pit. Morph a Larva into a Swarm Host.

## 41/100 sc2qa_000983

原标签：`ambiguous`；生成模型：`zai-org/GLM-5.2`。

**问题：** Can a Disruptor fire Purification Nova right away, or are there situations where it has to wait?

**原参考答案：** Purification Nova is always available as an active skill, so the Disruptor does not need to research or unlock it before use. However, the ability has a 14.3 second cooldown between activations. Additionally, if the Disruptor has just been dropped from a transport, it must wait through a 0.7 second charge time before it can activate Purification Nova.

**汇总分流：** 两方未发现答案实质问题，另一方有不同意见。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 无法核实 | 有效 | uncertain | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | two_hop | medium |

**A 的理由：** 净化新星自带无需研究，施放受冷却和运输卸载后的短暂延迟限制。0.7秒为近似表达，答案覆盖问题所问的等待情形。

未解决项：14.3秒的冷却口径未独立核实；不做版本审计。

候选答案：Purification Nova needs no research, but the Disruptor must wait for its cooldown and any brief delay after unloading from a transport.

**B 的理由：** 净化新星无需研究，且从运输机卸下后存在短暂施放限制，这些机制合理；但14.3秒冷却与我对该技能冷却的记忆不一致，未取得可访问数据，不能确认具体数值。

未解决项：需核实14.3秒冷却及0.7秒卸载延迟的原始时间口径；外部页面访问失败。

候选答案：Purification Nova requires no research, but cannot be used while on cooldown and has a short delay after unloading from a transport.

**C 的理由：** 答案正确区分天生拥有技能与技能冷却限制，并补充运输卸载后短暂充能。14.3秒冷却在实际访问的暴雪说明中有明确支持，不因其他时间数据而作版本审计。

未解决项：0.7秒卸载充能基于领域知识，未由官方页面单独验证。

候选答案：Purification Nova requires no research, but must be off cooldown. A Disruptor also has a short charge delay after being unloaded from a transport.

查阅来源：[1](https://news.blizzard.com/en-us/article/20975163/starcraft-ii-multiplayer-major-design-changes)

## 42/100 sc2qa_000046

原标签：`single_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** What is the shield capacity of the Hive?

**原参考答案：** The Hive does not have any shields. Its shield value is zero.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | not_applicable | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | not_applicable | single_hop | high |

**A 的理由：** 蜂巢为虫族建筑，没有护盾池；用0而非生命值回答护盾容量正确。

候选答案：A Hive has no shields; its shield capacity is 0.

**B 的理由：** 蜂巢属于虫族建筑，没有神族式护盾，护盾为0。答案直接回答这一属性。

候选答案：A Hive has no shields.

**C 的理由：** 主巢是虫族建筑，没有神族式护盾；护盾容量为0正确，无需把生命值混作护盾。

候选答案：A Hive has no shields; its shield capacity is 0.

## 43/100 sc2qa_000085

原标签：`two_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** How many minerals does a Terran Command Center cost, and what happens to its production capabilities when it lifts off?

**原参考答案：** The Command Center costs 400 minerals. When it lifts off, it cannot produce units or conduct research, and it must leave add-ons behind.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | not_applicable | single_hop | high |
| B | 部分正确 | 有效 | complete | single_hop | high |
| C | 部分正确 | 有效 | not_applicable | single_hop | high |

**A 的理由：** 指挥中心400矿且起飞后不能生产SCV正确；但它本来没有可挂的科技实验室或反应堆，说必须留下附件是把兵营工厂星港的特性套用到指挥中心。

候选答案：A Command Center costs 400 minerals. While lifted off, it cannot train SCVs. Command Centers do not use add-ons.

**B 的理由：** 指挥中心400矿且飞起不能训练SCV正确，但指挥中心本来就不接科技实验室或反应堆，‘必须留下附加建筑’是将其他人族建筑机制误套到基地。

候选答案：A Command Center costs 400 minerals. While flying, it cannot train SCVs or perform its landed upgrade actions. It does not use add-ons.

**C 的理由：** 指挥中心400矿且起飞不能训练SCV正确；但指挥中心本来不能连接科技实验室或反应堆，离开附属建筑是生产建筑通用描述，套用于指挥中心容易误导。

候选答案：A Command Center costs 400 minerals. While flying it cannot train SCVs or perform landed-only upgrades; it must land to resume those functions.

## 44/100 sc2qa_000219

原标签：`single_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** What is the base ability of the Terran Command Center regarding its Orbital Command form?

**原参考答案：** The Terran Command Center has a base ability to transform into an Orbital Command. This transformation is always available to the unit.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | single_hop | high |
| B | 存在错误 | 有效 | missing | single_hop | high |
| C | 部分正确 | 有效 | missing | two_hop | high |

**A 的理由：** 指挥中心能升级轨道指挥部，但并非始终无条件可用：需要兵营、150矿且指挥中心着陆可执行升级。

候选答案：A landed Command Center can upgrade to an Orbital Command after a Barracks has been built, for 150 minerals.

**B 的理由：** 升级轨道指挥部不是无条件始终可用；要有兵营、150矿、落地且能够进行升级的指挥中心。仅说always available会误导尚未满足科技和资源时即可变形。

候选答案：A landed Command Center can upgrade to an Orbital Command after a Barracks has been built, for 150 minerals.

**C 的理由：** 指挥中心可以升级轨道指挥部正确；但并非无条件随时可转，至少需要兵营、150矿且建筑着陆等。always available把拥有命令与满足执行条件混为一谈。

候选答案：A landed Command Center can upgrade into an Orbital Command after a Barracks has been built and the 150-mineral upgrade cost is available.

**玩家补充核查：** 轨道指挥部升级被无条件描述为始终可用。 COMMANDCENTER→ORBITALCOMMAND 项存在 BARRACKS 前置要求。 外部来源支持兵营前置，未在此核验具体价格。

来源：[S1](https://raw.githubusercontent.com/BurnySc2/python-sc2/develop/sc2/dicts/unit_train_build_abilities.py)

关系修正候选：A Command Center can be upgraded to an Orbital Command once the prerequisites are met, including a Barracks and sufficient resources; the upgrade is not unconditionally executable.

## 45/100 sc2qa_000435

原标签：`single_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** How much damage does the Flying Locust's weapon deal?

**原参考答案：** The Flying Locust's weapon deals 0 damage.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 无效 | not_applicable | single_hop | high |
| B | 部分正确 | 无效 | not_applicable | ambiguous | high |
| C | 部分正确 | 需澄清 | not_applicable | ambiguous | high |

**A 的理由：** 飞行蝗虫在空中不能攻击，必须降落才成为能作战的地面蝗虫；写成武器伤害0掩盖不存在可用空中武器这一差别。

候选答案：A flying Locust cannot attack while airborne. It must land before it can use its ground attack.

**B 的理由：** 飞行蝗虫在飞行状态不能进行普通攻击；回答0虽可表示无输出，却沿用了‘有一把伤害为0的武器’这一错误预设。需区分没有攻击与零伤害攻击。

候选答案：A Flying Locust cannot attack while flying; it must swoop down and become a ground Locust before attacking.

**C 的理由：** 飞行蝗虫在空中不能攻击，0若是数据库占位值应解释为无可用武器；称武器造成0伤害暗示其在执行无伤害攻击，与落地后才可攻击机制有区别。

候选答案：A flying Locust cannot attack while airborne. It must land before using the Locust's ground weapon.

## 46/100 sc2qa_000791

原标签：`ambiguous`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** When can the Disruptor's Purification Nova ability be used?

**原参考答案：** Purification Nova is an active skill that is always available to use, but it has a cooldown of 14.3 seconds after each activation. The ability requires a target point or range to be selected when activated. Additionally, if the Disruptor is dropped from a transport, there is a 0.7 second charge time before the ability can be used.

**汇总分流：** 两方未发现答案实质问题，另一方有不同意见。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 无法核实 | 有效 | uncertain | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | two_hop | medium |

**A 的理由：** 答案将自带技能与无条件连续施放区分开，提及冷却、目标点和卸载后延迟；足以回答何时能使用净化新星。

未解决项：14.3秒的精确冷却未外部核实，不据版本差异判错。

候选答案：Purification Nova can be activated at a target point when its cooldown and any brief post-unload delay have elapsed. It requires no research.

**B 的理由：** 目标点、冷却就绪与运输机卸载后的延迟确实都是可用性相关条件，但14.3秒冷却尚不能核定；不能因为是主动技能便认定任何时刻都可施放。

未解决项：14.3秒与0.7秒的确切口径未得到原始数据核查。

候选答案：Purification Nova can be cast at a valid point when the Disruptor is able to act, its cooldown is ready, and any post-unload delay has elapsed.

**C 的理由：** 净化新星不需研究但受冷却与卸载后充能限制；答案随后给出具体条件，因此always available可理解为默认解锁，未形成无条件可施放的结论。14.3有官方资料支持。

未解决项：0.7秒卸载充能未由所引官方页单独验证。

候选答案：It can be used when off cooldown and after any post-unload charge delay, by issuing a valid target-point command.

查阅来源：[1](https://news.blizzard.com/en-us/article/20975163/starcraft-ii-multiplayer-major-design-changes)

## 47/100 sc2qa_000301

原标签：`multi_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** What is the complete sequence of Protoss buildings required to construct an Observer?

**原参考答案：** To produce an Observer, a player must first construct a Warp Gate. The Warp Gate itself cannot be built directly; it requires a Gateway as a prerequisite. Therefore, the full chain begins with the Gateway, which unlocks the Warp Gate, which finally allows the production of the Observer.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 有效 | missing | multi_hop | high |
| C | 存在错误 | 有效 | missing | multi_hop | high |

**A 的理由：** 观察者从机械台生产，与折跃门无关；答案不仅漏控制芯核和机械台，还把折跃门改造当观察者的生产路径。

候选答案：Build a powered Gateway, then Cybernetics Core, then Robotics Facility. Train the Observer at the Robotics Facility; Warp Gate is not required.

**B 的理由：** 侦察器由机械台生产，不由折跃门解锁；折跃门研究和变形不是侦察器必要前置。答案将网关战斗单位生产路线误套在机械台单位上。

候选答案：Build a Gateway, Cybernetics Core, and Robotics Facility; train the Observer at the Robotics Facility. A Warp Gate is not required.

**C 的理由：** 侦察器由机械台生产，折跃门既不能生产侦察器，也不是其科技前置；实际链需要控制核心和机械台。

候选答案：Build a Gateway, then a Cybernetics Core, then a Robotics Facility. Produce the Observer at the Robotics Facility.

**玩家补充核查：** 把观察者与折跃门生产关系混淆。 ROBOTICSFACILITY 中有 OBSERVER 训练项。 外部来源支持生产关系错误。

来源：[S1](https://raw.githubusercontent.com/BurnySc2/python-sc2/develop/sc2/dicts/unit_train_build_abilities.py)

关系修正候选：An Observer is produced at a Robotics Facility. The technology path includes Gateway, Cybernetics Core, and Robotics Facility; a Warp Gate is not its production structure.

## 48/100 sc2qa_000153

原标签：`ambiguous`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** What does the Zealot's Charge ability require to activate?

**原参考答案：** Charge is a passive ability available after the Charge upgrade is researched at the Twilight Council. The Zealot must have a target enemy unit or structure within 4 range to initiate the charge, and the ability has a 7-second cooldown after use. Additionally, the Zealot needs clear ground pathing to reach its target.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | complete | single_hop | high |
| B | 部分正确 | 有效 | complete | single_hop | high |
| C | 部分正确 | 有效 | complete | two_hop | medium |

**A 的理由：** 研究、4距离、冷却及路径限制基本正确；冲锋是可主动下令且能自动施放的技能，称为被动会误导玩家认为不能手动控制或关闭自动施放。

候选答案：Research Charge at the Twilight Council. Charge is an autocast ability that can also be commanded manually; it needs a valid target within range, clear ground pathing, and a ready cooldown.

**B 的理由：** 冲锋研究、目标距离、冷却和可通行路径限制基本正确，但冲锋是可自动施放/手动使用的主动技能，不能简单称为被动能力。

未解决项：4射程与7秒的精确计时/距离边界未外查，不据此判数值错。

候选答案：After Charge is researched at the Twilight Council, a Zealot can use or autocast Charge against a valid ground target within charge range when the cooldown is ready and a path exists.

**C 的理由：** 研究冲锋、冷却与可行路径均相关；冲锋是可自动施放的技能且可手动下令，简单称为被动技能容易混淆玩家操作机制。

未解决项：题中4射程与7秒冷却数值未外查，未据此判错。

候选答案：Charge must be researched at the Twilight Council. It can then be ordered or autocast against a valid ground target in its activation range, when off cooldown and with a valid path.

## 49/100 sc2qa_000464

原标签：`two_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** How much armor does the Orbital Command have, and what are the energy cost and duration of its Scanner Sweep ability?

**原参考答案：** The Orbital Command has an armor value of 1. Its Scanner Sweep ability costs 50 energy to cast and lasts for 9 seconds. When activated, Scanner Sweep scans a target location on the map to temporarily reveal cloaked, burrowed, or hallucinated units.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 轨道指挥部基础护甲1、扫描50能量、约9秒持续符合通常数据；扫描提供指定区域视野与侦测，可揭露隐形潜地和幻象。

候选答案：An Orbital Command has 1 base armor. Scanner Sweep costs 50 energy and provides vision and detection for about 9 seconds.

**B 的理由：** 轨道指挥部1基础护甲，雷达50能量、约9秒侦测视野，与扫描能揭示隐形和潜地目标的机制一致。三个并列属性不是三跳依赖。

未解决项：持续时间存在取整口径，未单独外查。

候选答案：An Orbital Command has 1 base armor. Scanner Sweep costs 50 energy and provides detection and vision for about 9 seconds.

**C 的理由：** 轨道指挥部基础护甲1、扫描消耗50能量及约9秒持续时间符合所知；扫描同时提供区域视野和侦测，能揭示隐形/钻地与识别幻象的描述适当。

候选答案：An Orbital Command has 1 base armor. Scanner Sweep costs 50 energy and provides vision and detection for about 9 seconds.

## 50/100 sc2qa_000089

原标签：`two_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** What is the health of a liberator in Defender Mode, and what does the mode do?

**原参考答案：** The liberator has 180 health. In Defender Mode, it gains a long-ranged narrow attack that can inflict high single target damage, as well as bonus vision. However, it cannot move while in this mode.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | single_hop | high |
| B | 部分正确 | 有效 | missing | single_hop | high |
| C | 部分正确 | 有效 | missing | two_hop | high |

**A 的理由：** 180生命正确，对地高伤害及不能移动方向也正确；但防卫模式只攻击指定区域内地面目标，不能自由选择任意远处敌人，这个模式的核心限制被漏掉。

候选答案：A Liberator has 180 health. Defender Mode immobilizes it and lets it deal high single-target damage to ground units inside a designated target area.

**B 的理由：** 180生命正确，也说明架起后不能移动；但防卫模式只攻击指定防卫区域内的地面单位，不能对空且不能攻击建筑。仅说远程高单体伤害没有说明关键目标限制。

候选答案：A Liberator has 180 health. In Defender Mode it is stationary and attacks ground units within its designated zone with a powerful single-target weapon; it cannot attack air units or structures in this mode.

**C 的理由：** 解放者180生命和防卫模式固定不动正确；这一模式仅能攻击指定圆形区域内的地面单位，是区别于对空模式的核心条件。答案只说长程窄攻击没有明确目标层及区域。

候选答案：A Liberator has 180 health. Defender Mode immobilizes it and enables powerful single-target attacks against ground units inside its designated target area.

## 51/100 sc2qa_000806

原标签：`single_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** What is the range of the Terran Siege Tank's primary weapon?

**原参考答案：** The Terran Siege Tank's primary weapon has a range of 7.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 需澄清 | missing | ambiguous | high |
| B | 部分正确 | 需澄清 | missing | ambiguous | high |
| C | 部分正确 | 需澄清 | missing | ambiguous | high |

**A 的理由：** 7是坦克模式射程；攻城模式射程13且有最小射程。题干primary weapon没有指明模式，答案需限定7对应移动模式。

候选答案：In tank mode the Siege Tank has range 7. In siege mode it has maximum range 13 and a minimum range.

**B 的理由：** 7是坦克移动模式的武器射程，架起后射程为13且有最小射程。题目只写Siege Tank primary weapon，未指定模式，答案必须标明使用哪种形态。

候选答案：A Siege Tank has range 7 in Tank Mode and range 13 in Siege Mode, with a minimum range in Siege Mode.

**C 的理由：** 坦克常规模式主炮射程7正确，攻城模式则为13且有最小射程。题目未说明形态，答案应明确7适用于未架起模式。

候选答案：A Siege Tank has range 7 in tank mode and maximum range 13 in siege mode; siege mode also has a minimum range.

## 52/100 sc2qa_000617

原标签：`single_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** What is the attack cooldown of the Photon Cannon in StarCraft II?

**原参考答案：** The Photon Cannon has an attack cooldown of 1.25 seconds.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | medium |

**A 的理由：** 光子炮1.25秒符合基础数据计时的攻击间隔；不将其与DPS、伤害或加速游戏下秒数混为一项。

未解决项：题目未给游戏速度；未外部校验时间换算。

候选答案：A Photon Cannon has a base attack cooldown of 1.25 seconds in the base-time convention.

**B 的理由：** 1.25秒是光子炮通常列出的基础武器攻击间隔，答案给出了秒单位，未误当建造时间或攻击射程。

未解决项：实际速度下的秒数需明确计时口径。

候选答案：A Photon Cannon's base weapon cooldown is 1.25 game seconds in the stated time scale.

**C 的理由：** 光子炮攻击间隔1.25游戏秒符合常见原始数据口径；题目直接问攻击冷却，未把此值当作每秒伤害。

未解决项：未指定游戏速度，实际时间口径需随数据说明。

候选答案：A Photon Cannon has an attack period of 1.25 game-time seconds in this data scale.

## 53/100 sc2qa_000986

原标签：`ambiguous`；生成模型：`zai-org/GLM-5.2`。

**问题：** Can the Battlecruiser use Tactical Jump freely at any time, or does it need to meet certain conditions first?

**原参考答案：** The Battlecruiser's Tactical Jump warps the user to a target location, and no explicit cooldown or energy cost is stated in the ability text. However, activation requires a target location, as the ability's stated constraint is target or range. Before warping, the Battlecruiser enters a 1 second vulnerable phase and then vanishes from the map. So while no resource gate is explicitly mentioned, the ability still depends on selecting a valid target location within range.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | single_hop | high |
| B | 存在错误 | 有效 | missing | single_hop | high |
| C | 存在错误 | 有效 | missing | two_hop | high |

**A 的理由：** 战术折跃有较长冷却，是不能随时连续使用的核心限制；答案根据未提供的技能文本称无明确冷却，还暗示通常射程限制，遗漏全图折跃性质。

未解决项：未提供原始ability text，无法验证其是否真的省略了冷却；此处审核实际机制。

候选答案：Tactical Jump requires a ready cooldown and a legal target location. It costs no energy and can reach across the map, but includes a brief vulnerable delay before teleporting.

**B 的理由：** 战术跳跃有冷却限制，不能从技能文字未列冷却推出没有资源或冷却门槛；它能跳到地图目标点，不要求普通意义的有限施法射程。答案避开了题目的关键可用性限制。

未解决项：具体冷却秒数未外查，因此建议答案不报数。

候选答案：Tactical Jump requires its cooldown to be ready and a valid destination. It has no energy cost, but has a vulnerable wind-up and cannot be used repeatedly without waiting for cooldown.

**C 的理由：** 未在技能文字列出冷却不能推出无需冷却。战术跳跃有约71秒冷却，是自由施放问题的核心限制；并无普通短程施法距离限制。1秒脆弱阶段有官方资料支持，但不能补足所漏冷却。

候选答案：Tactical Jump costs no energy but must be off its roughly 71-second cooldown. Choose a valid destination anywhere on the map; the Battlecruiser undergoes a brief vulnerable phase before completing the jump.

查阅来源：[1](https://news.blizzard.com/en-us/article/23227811/starcraft-ii-4-11-0-patch-notes)；[2](https://news.blizzard.com/en-us/article/23190445/starcraft-ii-balance-update-october-29-2019)

## 54/100 sc2qa_000055

原标签：`two_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** How much shield does the unit that can create creep tumors have?

**原参考答案：** The unit that can create creep tumors is the Zerg Queen. It has 0 shield.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 需澄清 | complete | ambiguous | high |
| B | 未发现实质问题 | 有效 | complete | two_hop | high |
| C | 未发现实质问题 | 有效 | not_applicable | two_hop | high |

**A 的理由：** 女王可制造菌毯瘤且无护盾，所以答案数值正确；但已有菌毯瘤也能传播新的菌毯瘤，所谓能制造的unit并非唯一指代。

候选答案：A Queen can create Creep Tumors and has 0 shields. Existing Creep Tumors can also spread new tumors.

**B 的理由：** 由‘能铺菌毯瘤的单位’识别虫后，再读取其护盾；虫后确实没有护盾。现有菌毯瘤也能扩散，但其作为建筑同样无护盾，不影响所问数值。

候选答案：The Queen can create Creep Tumors and has no shields (0).

**C 的理由：** 先由放置菌毯肿瘤技能识别女王，再查女王护盾0，是两步关系；虫族女王没有护盾这一结论正确。

候选答案：The Queen can create Creep Tumors and has no shields (0).

## 55/100 sc2qa_000345

原标签：`multi_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** What is the complete building prerequisite chain required to produce a Twilight Council?

**原参考答案：** To produce a Twilight Council, a player must first build a Gateway. Once the Gateway is constructed, it enables the production of a Cybernetics Core. Finally, the Cybernetics Core is required to construct the Twilight Council itself.

**汇总分流：** 两方未发现答案实质问题，另一方有不同意见。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | multi_hop | high |
| B | 未发现实质问题 | 有效 | complete | two_hop | high |
| C | 未发现实质问题 | 有效 | complete | two_hop | high |

**A 的理由：** 传送门→控制芯核→暮光议会的科技关系正确；题目强调complete，还需水晶塔供能才能建造运行这些建筑，答案没有说明这一必要建筑。

候选答案：Build a Pylon for power, then a Gateway, Cybernetics Core, and Twilight Council.

**B 的理由：** 科技前置顺序网关—控制核心—暮光议会正确。这里是建筑间两条依赖关系，不应仅按出现三个建筑判三跳。实际神族建筑还需满足供能等通用建造条件。

候选答案：Build a Gateway, then a Cybernetics Core, then a Twilight Council.

**C 的理由：** 兵营—控制核心—暮光议会为正确的直接科技链；普通神族建筑供能属于常规建造背景，不改变该科技依赖顺序。

候选答案：Gateway → Cybernetics Core → Twilight Council, with the required power and resources.

## 56/100 sc2qa_000461

原标签：`two_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** When a Queen uses Spawn Larva on a Hatchery, Lair, or Hive, how much do the resulting larvae cost?

**原参考答案：** Queens can use Spawn Larva on a Hatchery, Lair, or Hive to add extra larvae. In Legacy of the Void, this usually creates three larvae after 29 seconds. The Larva units produced cost zero minerals, zero gas, and zero supply.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | two_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | two_hop | high |

**A 的理由：** 注卵得到的幼虫本身不花矿气人口，不能把女王技能能量或未来孵化单位费用记在幼虫身上；答案清楚区分了两者。

未解决项：附加三幼虫和29秒未逐项外部核实。

候选答案：The resulting larvae themselves cost 0 minerals, 0 gas, and 0 supply. Spawn Larva uses Queen energy, and units later morphed from the larvae have their own costs.

**B 的理由：** 注卵产生的幼虫自身不扣矿、气或人口；需区分虫后的施法能量与幼虫单位资源成本，答案对此没有混淆。额外29秒不是所问成本所依赖的条件。

候选答案：The larvae themselves cost 0 minerals, 0 gas, and 0 supply; Spawn Larva uses the Queen's energy.

**C 的理由：** 注卵由女王耗能产生额外幼虫，但幼虫本身不消耗矿气与人口；答案正确区分技能能量成本和幼虫单位资源成本。3个与29秒属额外背景，不作版本差异审计。

候选答案：The spawned Larvae themselves cost 0 minerals, 0 gas and 0 supply; the Queen's Spawn Larva ability costs energy.

## 57/100 sc2qa_000114

原标签：`multi_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** What is the building prerequisite chain required to produce a Protoss Observer?

**原参考答案：** To produce a Protoss Observer, you first need a Cybernetics Core. The Cybernetics Core requires a Gateway, a Protoss building. Therefore, the building chain is Gateway, then Cybernetics Core, then Observer.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 有效 | missing | multi_hop | high |
| C | 存在错误 | 有效 | missing | multi_hop | high |

**A 的理由：** 传送门到控制芯核正确，但控制芯核不直接生产观察者；必须再建机械台并在那里生产。

候选答案：Build Gateway → Cybernetics Core → Robotics Facility, with Pylon power. Train the Observer at the Robotics Facility.

**B 的理由：** 控制核心不能直接生产侦察器；必需的生产建筑机械台完全遗漏，所给Gateway—Core—Observer链不可执行。

候选答案：Build a Gateway, Cybernetics Core, and Robotics Facility; the Robotics Facility produces Observers.

**C 的理由：** 控制核心不能直接生产侦察器；还必须建机械台作为生产建筑。答案将控制核心后直接接侦察器，使生产链不成立。

候选答案：Gateway → Cybernetics Core → Robotics Facility → Observer.

**玩家补充核查：** 观察者科技路径遗漏其生产建筑机械台。 观察者的生产者为 ROBOTICSFACILITY，该建筑的前置为 CYBERNETICSCORE。 外部来源支持遗漏生产建筑。

来源：[S1](https://raw.githubusercontent.com/BurnySc2/python-sc2/develop/sc2/dicts/unit_train_build_abilities.py)

关系修正候选：The path includes Gateway, Cybernetics Core, and Robotics Facility. The Observer is trained at the Robotics Facility.

## 58/100 sc2qa_000491

原标签：`two_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** How much armor does the Roach have, and what effect does its Ravager Morph ability provide?

**原参考答案：** The Roach has an armor value of 1. It possesses the Ravager Morph ability, which is always available. This ability allows the Roach to morph into a Ravager and costs 1 supply.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | single_hop | high |
| B | 部分正确 | 有效 | missing | single_hop | high |
| C | 部分正确 | 有效 | missing | two_hop | high |

**A 的理由：** 蟑螂1护甲与变异破坏者效果正确；但变异不只需额外1人口，还需25矿75气及变异时间，称always available容易掩盖资源与人口门槛。

候选答案：A Roach has 1 base armor. It can morph into a Ravager for 25 minerals, 75 gas, and 1 additional supply, gaining the Ravager’s stats and Corrosive Bile ability.

**B 的理由：** 蟑螂基础护甲1与变为破坏者的效果正确；但变形还需25矿75气及额外1人口空间。写成始终可用并仅说花1人口，会误导资源不足时也能变形。

候选答案：A Roach has 1 base armor. Ravager Morph turns it into a Ravager for 25 minerals, 75 gas, and 1 additional supply, provided those resources and supply are available.

**C 的理由：** 蟑螂护甲1、变身破坏者及额外占1人口正确；但变形还需25矿75气，不能以always available暗示无资源条件，单列1人口会造成完整费用的错误印象。

候选答案：A Roach has 1 base armor. Ravager Morph transforms it into a Ravager for 25 minerals, 75 gas and 1 additional supply.

## 59/100 sc2qa_000394

原标签：`ambiguous`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** Can the Adept attack an air unit, or is its weapon restricted to ground targets only?

**原参考答案：** The Adept's weapon targets ground units exclusively, as indicated by its attributes. Both the unit's general targeting and its specific weapon data restrict attacks to ground targets. Consequently, the Adept cannot engage air units with its current configuration.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 使徒普攻只能打地面目标，答案没有把灵能转移的影子或其自身属性当作对空能力。

候选答案：An Adept can attack only ground targets and cannot attack air units.

**B 的理由：** 使徒普通武器仅对地，不能攻击空军；答案没有把灵能转移影子或移动能力当作对空武器。

候选答案：An Adept's weapon attacks ground targets only; it cannot attack air units.

**C 的理由：** 使徒只能攻击地面，答案直接否定对空且没有把灵能转移误作对空手段。两次描述同一目标限制不增加推理深度。

候选答案：An Adept attacks ground targets only and cannot attack air units.

## 60/100 sc2qa_000473

原标签：`two_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** What is the shield value of the Sentry, and what effect does its Guardian Shield ability have?

**原参考答案：** The Sentry has a shield value of 40. Its Guardian Shield ability creates a radius 4.5 aura that reduces incoming ranged damage to friendly units by 2. This ability costs 75 energy to cast and has a duration and cooldown of 12.86 seconds.

**汇总分流：** 两方未发现答案实质问题，另一方有不同意见。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 部分正确 | 有效 | missing | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 哨兵护盾40，守护者之盾是对友方的远程伤害每次减2的范围光环而非增加护盾容量；答案两者区分正确。

未解决项：12.86秒持续与冷却尚未以原始游戏数据逐项核实。

候选答案：A Sentry has 40 shields. Guardian Shield costs 75 energy and creates a radius-4.5 aura that reduces incoming ranged damage to friendly units by 2.

**B 的理由：** 哨兵40护盾、75能量、4.5光环及减2范围武器伤害的主干正确；应明确是远程武器攻击，不能让‘incoming ranged damage’泛指法术伤害。12.86同时作持续与冷却也尚未核定。

未解决项：技能持续时间与冷却均写12.86秒，未获得可用外部数据确认。

候选答案：A Sentry has 40 shields. Guardian Shield costs 75 energy and gives nearby friendly units a radius-4.5 aura reducing damage from ranged weapon attacks by 2; it does not reduce spell damage.

**C 的理由：** 哨兵护盾40、守护者之盾半径4.5、减少友军受到的远程伤害2及75能量均符合所知机制。护盾容量与技能减伤是并列属性，不是两跳推导。

候选答案：A Sentry has 40 shields. Guardian Shield creates a radius-4.5 aura that reduces incoming ranged damage to friendly units by 2.

## 61/100 sc2qa_000557

原标签：`ambiguous`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** How much energy does it cost to create a Creep Tumor?

**原参考答案：** The energy cost to create a Creep Tumor depends on whether the Queen or an existing Creep Tumor is creating it. When the Queen casts the ability, it costs 25 energy. However, when an existing Creep Tumor creates an additional Creep Tumor, it does so with no energy cost. Both methods take 11 seconds to complete.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 答案准确区分女王造瘤25能量与已有菌毯瘤扩散零能量，避免把两种来源当成同一消耗。11秒是附加施工时间。

未解决项：附加11秒的时间口径未外部核查。

候选答案：A Queen spends 25 energy to create a Creep Tumor. Spreading a new tumor from an existing Creep Tumor costs no energy.

**B 的理由：** 答案正确区分虫后铺菌毯瘤需要25能量，而已成熟菌毯瘤扩散不耗能量；没有把扩散次数或冷却当作能量成本。

未解决项：附加11秒建造时长未单独外查。

候选答案：A Queen spends 25 energy to create a Creep Tumor. An existing Creep Tumor creates its offspring with no energy cost.

**C 的理由：** 答案正确区分女王放瘤25能量与菌瘤扩散不耗能量；11秒是生成菌瘤过程，不能与已生长菌瘤再次扩散的等待冷却混淆，答案未明确混同。

候选答案：A Queen spends 25 energy to create a Creep Tumor. A Creep Tumor can create another one without an energy cost.

## 62/100 sc2qa_000091

原标签：`two_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** What is the damage and range of the Planetary Fortress's ground weapon, and what does its Load ability do?

**原参考答案：** The Planetary Fortress's ground weapon deals 40 damage with a range of 6. Its Load ability allows the Terran player to load SCVs into a Command Center or Planetary Fortress.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 行星要塞基础对地40伤害6射程，Load允许装入SCV以保护工人；没有误说可装入陆战队或能起飞。

候选答案：The Planetary Fortress deals 40 base ground damage at range 6. Load lets it garrison SCVs for protection.

**B 的理由：** 行星要塞基础地面武器40伤害6射程正确；Load指装载SCV而非把普通作战部队当碉堡驻军。装载并不赋予行星要塞起飞能力。

未解决项：未外查装载人数或额外升级，因此建议不添加这些数值。

候选答案：A Planetary Fortress's ground weapon deals 40 base damage at range 6. Load allows SCVs to be garrisoned inside the structure.

**C 的理由：** 行星要塞基础武器伤害40射程6正确；装载SCV是指挥中心及行星要塞的工人装载功能，不是让其装任意步兵。两项是并列属性。

候选答案：The Planetary Fortress's ground weapon deals 40 base damage at range 6. Load allows it to garrison SCVs.

## 63/100 sc2qa_000430

原标签：`single_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** What is the weapon cooldown of the Brood Lord?

**原参考答案：** The weapon cooldown of the Brood Lord is 1.79.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | uncertain | single_hop | medium |
| B | 部分正确 | 有效 | missing | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | medium |

**A 的理由：** 1.79可对应巢虫领主的常用攻击间隔，但答案未给秒和计时口径，作为weapon cooldown量值不完整。

未解决项：未核实具体游戏速度下的1.79换算。

候选答案：The Brood Lord’s attack cooldown is about 1.79 seconds under the stated game-speed convention.

**B 的理由：** 1.79与巢虫领主常见攻击间隔数字相符，但没有标单位，也未说明实际时间/游戏时间口径，作为独立答案不完整。

未解决项：需标清秒与计时速度口径。

候选答案：A Brood Lord's weapon cooldown is approximately 1.79 seconds in the stated time scale.

**C 的理由：** 巢虫领主攻击间隔约1.79秒符合常用快速度资料值；没有把生成的巢虫攻击间隔当作巢虫领主武器周期。

未解决项：答案未附单位，建议数据集统一时间单位说明。

候选答案：The Brood Lord's attack period is approximately 1.79 seconds in this timing scale.

## 64/100 sc2qa_000565

原标签：`ambiguous`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** Can a Spine Crawler attack an enemy if it is not specified whether the enemy is on the ground or in the air?

**原参考答案：** A Spine Crawler can only attack ground units, as both its targeting and its weapon are restricted to ground. If the enemy is an air unit, the Spine Crawler cannot attack it. Therefore, whether the Spine Crawler can engage the enemy depends entirely on whether the target is on the ground or in the air.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 需澄清 | missing | ambiguous | high |
| B | 部分正确 | 需澄清 | missing | ambiguous | high |
| C | 部分正确 | 需澄清 | missing | ambiguous | high |

**A 的理由：** 地刺只对地正确，但结论称entirely取决于目标层过强；拔起的地刺不能攻击，还需扎根、射程和视野，不能只由地面属性确定。

候选答案：A rooted Spine Crawler can attack visible ground enemies within range; it cannot attack air units or attack while uprooted. Clarify the target layer.

**B 的理由：** 地刺仅对地正确，但是否能攻击并不‘完全取决于’目标层；必须扎根且目标位于射程并可被攻击。爬行状态即使遇到地面敌人也不能开火。

候选答案：A rooted Spine Crawler can attack a valid ground target within range, but cannot attack air units. An uprooted Spine Crawler cannot attack.

**C 的理由：** 脊针爬虫只能对地正确；但其是否能攻击还取决于是否扎根，拔起状态不能攻击，因此不能说完全只取决于敌方地面/空中层级。

候选答案：A rooted Spine Crawler can attack ground targets in range, but cannot attack air targets. An uprooted Spine Crawler cannot attack.

## 65/100 sc2qa_000398

原标签：`ambiguous`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** Can the Immortal attack an enemy unit if the unit's ground-or-air layer is not specified?

**原参考答案：** The Immortal's attributes and weapon target only ground units. If the target unit's layer is unspecified, it is not guaranteed that the Immortal can attack it. The condition must be clarified to confirm the target is on the ground layer.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 需澄清 | complete | ambiguous | high |
| B | 未发现实质问题 | 需澄清 | complete | ambiguous | high |
| C | 未发现实质问题 | 需澄清 | complete | ambiguous | high |

**A 的理由：** 不朽者普攻只对地；答案只主张需确认目标层才能保证可攻击，没有把不明确目标强行判为可攻击。

候选答案：An Immortal can attack only ground targets, so clarify whether the target is on the ground.

**B 的理由：** 不朽者普通武器只能对地，未知目标层不能保证可攻击；答案正确回答目标层这一缺失条件，未声称对地是所有作战条件的充分条件。

候选答案：An Immortal attacks ground targets only; the target's layer must be known to determine whether its weapon can engage it.

**C 的理由：** 不朽者武器只能对地，答案准确说明目标层级未知时不能保证能攻击。该不确定来自目标信息，而非需要更多跳数。

候选答案：An Immortal can attack only ground targets, so the target must be confirmed as ground.

## 66/100 sc2qa_000880

原标签：`two_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** What is the armor value of a Terran Bunker, and what are the effects and restrictions of its Salvage ability?

**原参考答案：** The Terran Bunker has an armor value of 1. Its Salvage ability is always available and removes the structure, returning 75% of its mineral and vespene gas cost. The Salvage process cannot be aborted once started, and a Bunker cannot be salvaged while units are still inside it.

**汇总分流：** 至少两方认为答案无法核实。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 无法核实 | 有效 | uncertain | single_hop | low |
| C | 无法核实 | 有效 | uncertain | two_hop | medium |

**A 的理由：** 地堡1基础护甲与回收返还75%费用、不可撤回和需先卸空的限制相符；地堡本身无气费，写气费返还不造成实际额外收益。

未解决项：装载状态限制未用原始游戏数据独立核实。

候选答案：A Bunker has 1 base armor. Salvage removes an empty Bunker and returns 75% of its cost; once started it cannot be canceled.

**B 的理由：** 碉堡1护甲、回收拆除并返还75%费用的主体机制合理；但‘不能取消’和‘内部有单位便不能回收’是具体操作限制，我未能可靠核定，不能把它们当作已验证条件。

未解决项：需核验回收能否中断及是否要求先卸载驻军；无实际外部证据。

候选答案：A Bunker has 1 base armor. Salvage dismantles it and refunds 75% of its construction cost; the exact cancellation and occupancy restrictions should be checked against ability data.

**C 的理由：** 地堡基础护甲1、回收返还75%资源的主干正确。载员是否禁止启动回收及受伤是否中断回收，现有记忆与所见摘要不一致；不能把不可由玩家取消等同于任何情况都不会中断，需核实这两项条件。

未解决项：尚未直接验证载员限制和受伤中断规则，保留不确定。

## 67/100 sc2qa_000037

原标签：`single_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** How long does it take to train an SCV?

**原参考答案：** The SCV requires a production time of 17 seconds.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | medium |

**A 的理由：** SCV17秒对应基础时间口径的训练时长；无需引入不相关的指挥中心升级前置。

未解决项：未给游戏速度，不据换算差异判错。

候选答案：An SCV takes 17 seconds to train in the base-time convention.

**B 的理由：** 17秒是SCV常见基础训练时间口径；答案有秒单位并直接回答训练时间。没有发现训练建筑或成本混淆。

未解决项：实际游戏速度下秒数需明确换算口径。

候选答案：An SCV takes 17 game seconds to train in the stated time scale.

**C 的理由：** SCV训练17游戏时间秒符合常见Normal数据口径；答案直接给生产周期，未发现实质机制错误。

未解决项：实际墙钟秒数须按游戏速度解释。

候选答案：An SCV takes 17 game-time seconds to train in this timing scale.

## 68/100 sc2qa_000657

原标签：`two_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** What is the mineral cost of an Orbital Command, and can it still produce units while lifted off?

**原参考答案：** An Orbital Command costs 150 minerals. When it lifts off, it can fly but cannot produce units or conduct research and must leave any add‑ons behind.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | single_hop | high |
| B | 部分正确 | 需澄清 | missing | ambiguous | high |
| C | 部分正确 | 需澄清 | missing | single_hop | high |

**A 的理由：** 150矿是从指挥中心升级的增量费用而非含指挥中心总价；起飞不能训练SCV正确，但轨道指挥部不能挂附件，留下附件说法错误。

候选答案：The Orbital Command upgrade costs 150 minerals, in addition to the Command Center’s 400 minerals. It cannot train SCVs while flying and does not use add-ons.

**B 的理由：** 150矿是从指挥中心升级轨道的增量费用，若算总建造成本需加400矿；飞起不能产SCV正确，但轨道指挥部不使用附加建筑，不能说要留下附加建筑。

候选答案：The Orbital Command upgrade costs 150 minerals in addition to the Command Center's 400 minerals. A flying Orbital Command cannot train SCVs and does not use add-ons.

**C 的理由：** 150矿是轨道指挥部升级增量，若含指挥中心总投资为550矿，题干成本口径可澄清。起飞不能生产正确，但轨道指挥部不能连接生产附属建筑，离开附属建筑的说法不适用。

候选答案：The Orbital Command upgrade costs 150 minerals, or 550 minerals including the Command Center. While flying, it cannot train SCVs.

## 69/100 sc2qa_000897

原标签：`two_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** What are the targeting restrictions of the Terran Liberator's Fighter Mode, and what are the damage and range stats of its ground-targeting weapon?

**原参考答案：** When the Terran Liberator is in Fighter Mode, it can move but is restricted to only targeting air units. The Liberator also has a weapon that targets ground units, which deals 75 damage and has a range of 10.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | single_hop | medium |
| B | 部分正确 | 有效 | missing | single_hop | medium |
| C | 部分正确 | 有效 | missing | two_hop | high |

**A 的理由：** 战斗机模式只对空并可移动正确；对地75伤害10射程应明确只在防卫模式、仅对指定区域内地面目标生效，不能让人理解战斗机模式同时可用该武器。

未解决项：对地10射程的具体数据口径未外部核实。

候选答案：Fighter Mode is mobile and attacks only air. The ground weapon is available in Defender Mode, deals 75 base damage, and can fire only at ground targets in its designated area.

**B 的理由：** 战机模式只能对空且可移动正确；对地武器只能在防卫模式使用，不能将其并列成战机模式下可用武器。75伤害与10射程还需说明基础值和模式口径。

未解决项：10射程与防卫区域/武器有效覆盖距离的定义未提供，需查原始字段。

候选答案：In Fighter Mode, a Liberator moves and attacks air targets only. Its separate anti-ground weapon is used in stationary Defender Mode against ground units in the designated zone.

**C 的理由：** 战斗机模式只能对空且可移动正确；75伤害射程10描述的是防卫模式地面武器，必须说明切换模式及只能攻击指定区域内地面单位，否则易读成战斗机模式也能用这门炮。

候选答案：Fighter Mode attacks only air units. In Defender Mode, the Liberator uses its ground weapon, dealing 75 base damage with the stated range of 10, restricted to its designated ground target area.

## 70/100 sc2qa_000907

原标签：`multi_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** What Terran building prerequisite must be satisfied before a Reactor can be produced from a Starport, and what resources does the Reactor require?

**原参考答案：** A Reactor costs 50 minerals and 50 gas to produce and can be built from a Starport. The Starport itself requires a Factory as a prerequisite building. The Factory is a Terran building, so a player must construct a Factory before a Starport can be built to produce the Reactor.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | two_hop | high |
| B | 未发现实质问题 | 有效 | complete | two_hop | high |
| C | 未发现实质问题 | 有效 | complete | two_hop | high |

**A 的理由：** 星港需工厂，星港可造50矿50气反应堆；两步依赖与资源字段对应准确，未把反应堆与科技实验室费用混淆。

候选答案：A Factory is required before building a Starport. The Starport can then build a Reactor for 50 minerals and 50 gas.

**B 的理由：** 星港需重工厂解锁，星港可建50矿50气的反应堆；答案正确区分星港上游科技和反应堆自身成本，没有把反应堆当星港前置。

候选答案：A Factory is required before building a Starport. A Reactor built by the Starport costs 50 minerals and 50 gas.

**C 的理由：** 兵工厂是星港直接科技前置，星港可以建50矿50气的反应堆；答案没有把附属建筑说成兵工厂直接生产星港，依赖关系清楚。

候选答案：A Factory is required to build the Starport; the Starport can build a Reactor for 50 minerals and 50 gas.

## 71/100 sc2qa_000861

原标签：`two_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** How many minerals and gas does it cost to produce the unit with the EMP Shot ability, and how much energy does EMP Shot cost to use?

**原参考答案：** The unit with the EMP Shot ability is the Ghost, which costs 200 minerals and 100 gas to produce. The EMP Shot ability costs 75 energy to use. When cast, it drains 100 shields from protoss units and 100 energy from units in the area of effect.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | two_hop | medium |
| B | 未发现实质问题 | 有效 | complete | two_hop | medium |
| C | 未发现实质问题 | 有效 | complete | two_hop | medium |

**A 的理由：** EMP技能指向幽灵，再读取该单位资源成本与EMP的75能量，依赖为技能→单位→造价。200矿100气是一种可识别的数据值，不按版本差异判错；EMP范围削盾削能量描述合理。

未解决项：未对资源数值作原始数据外部核实；本次明确不审版本。

候选答案：EMP Shot is a Ghost ability and costs 75 energy. In the stated cost data, the Ghost costs 200 minerals and 100 gas.

**B 的理由：** 先由EMP识别幽灵，再读取其资源成本及技能能量费；75能量与EMP范围削减护盾/能量机制成立，未发现单位与技能归属混淆。不做版本审计。

未解决项：所给200矿100气未提供外部原始成本表逐项认证。

候选答案：The unit is the Ghost. In the stated cost basis it costs 200 minerals and 100 gas, and EMP Shot costs 75 energy.

**C 的理由：** 由EMP技能识别幽灵，再查200矿100气造价构成两步；EMP75能量以及范围内移除100护盾与100能量是所知可成立的数据组合，不因其他造价组合审计版本。

未解决项：未提供原始单位数据，造价仅按所知可成立口径判断。

候选答案：The Ghost costs 200 minerals and 100 gas in the stated data; EMP Shot costs 75 energy.

## 72/100 sc2qa_000647

原标签：`single_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** What is the effect of the Terran Reaper's Jet Pack ability?

**原参考答案：** The Jet Pack ability is always available. It allows Reapers to jump up and down cliffs.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 死神喷气背包允许上下适当的悬崖，不需另研究或消耗能量；答案直接描述其通行机制。

候选答案：Jet Pack lets Reapers jump up and down traversable cliff edges.

**B 的理由：** 死神喷气背包的核心效果是上下悬崖，无需额外研究，答案准确描述其地形机动性。它并不意味着死神成为空中单位。

候选答案：Jet Pack lets Reapers jump up and down cliffs.

**C 的理由：** 喷气背包使死神可跨越允许跳跃的高低地悬崖，是默认移动机制；答案不将其误解为能飞行或可无视全部地形。

候选答案：Jet Pack lets Reapers jump up and down traversable cliffs.

## 73/100 sc2qa_000675

原标签：`two_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** How much total damage does a High Templar's Psionic Storm deal, and what is the High Templar's armor value?

**原参考答案：** Psionic Storm deals a total of 80 damage in small packets over 2.85 seconds, hitting both air and ground units. The High Templar itself has an armor value of 0.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 风暴完整持续伤害80、可伤地空及高阶圣堂武士基础护甲0相符；总伤害默认目标完整承受整个风暴，答案用over说明持续结算。

未解决项：2.85秒为近似计时，未独立核实速度口径。

候选答案：Psionic Storm deals up to 80 total damage over its duration to air and ground units. A High Templar has 0 base armor.

**B 的理由：** 心灵风暴完整命中总计80伤害，分段作用于地空单位；高阶圣堂武士基础护甲0。答案没有把单段伤害误当总伤害，2.85秒属于持续时间口径。

未解决项：具体持续时间的取整与计时口径未外查。

候选答案：Psionic Storm deals up to 80 total damage over its duration to units that remain in the area. A High Templar has 0 base armor.

**C 的理由：** 灵能风暴完整命中总伤害80、约2.85秒分段伤害且可伤害空地单位，高阶圣堂基础护甲0均正确；持续伤害总量以目标留在风暴内为隐含条件。

候选答案：A full Psionic Storm deals 80 damage over about 2.85 seconds to air and ground units that remain in it. A High Templar has 0 base armor.

## 74/100 sc2qa_000005

原标签：`single_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** Does the Engineering Bay have a shield stat?

**原参考答案：** The Engineering Bay has a shield value of 0.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | not_applicable | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | not_applicable | single_hop | high |

**A 的理由：** 工程站是无人族原生护盾的建筑，0护盾回答正确；数值0应理解为无护盾，而非消耗完了的护盾。

候选答案：An Engineering Bay has no shields; its shield value is 0.

**B 的理由：** 工程站是人族建筑，没有护盾池；0是对所问护盾属性的直接回答。

候选答案：An Engineering Bay has no shields (0).

**C 的理由：** 工程站没有护盾；用护盾数值0回答该属性问题准确，无需将建筑护甲混进护盾。

候选答案：An Engineering Bay has no shields; its shield value is 0.

## 75/100 sc2qa_000866

原标签：`two_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** What mobility does the Terran Reaper's Jet Pack provide, and what type of units can it target?

**原参考答案：** The Terran Reaper's Jet Pack allows it to jump up and down cliffs. However, the Reaper is restricted to targeting ground units.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 死神喷气背包的翻越悬崖能力与普攻只对地是两个并列属性；答案没有从可跳崖推导出可攻击空中。

候选答案：Jet Pack lets Reapers traverse cliffs. Reaper attacks can target only ground units.

**B 的理由：** 喷气背包提供上下悬崖机动，死神普通武器只对地；移动能力与攻击目标层是并列属性，没有被错误串成能对空的推论。

候选答案：Jet Pack lets a Reaper jump cliffs; its weapons can attack ground units only.

**C 的理由：** 死神喷气背包跨悬崖、常规武器只对地两项均正确；机动能力不会自动增加对空能力，两项是并列机制查询。

候选答案：Jet Pack lets a Reaper jump up and down cliffs. Its weapons target ground units only.

## 76/100 sc2qa_000515

原标签：`multi_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** What Terran building is required as a prerequisite for a Starport to produce a Reactor, and what is the cost of the Reactor?

**原参考答案：** To produce a Reactor from a Starport, a Factory must first be constructed as a prerequisite. The Factory is a Terran building required for the Starport. The Reactor costs 50 minerals and 50 gas to produce.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | two_hop | high |
| B | 未发现实质问题 | 有效 | complete | two_hop | high |
| C | 未发现实质问题 | 有效 | complete | two_hop | high |

**A 的理由：** 工厂为星港前置、星港可造反应堆50矿50气，两步建筑依赖正确；问题没有要求从零列全部人族建筑。

候选答案：Build a Factory to unlock the Starport. A Reactor built by the Starport costs 50 minerals and 50 gas.

**B 的理由：** 重工厂是星港科技前置，反应堆由星港建造并花50矿50气；回答以正确方向串联前置与生产建筑。

候选答案：Build a Factory before the Starport. The Starport can build a Reactor for 50 minerals and 50 gas.

**C 的理由：** 兵工厂解锁星港、星港建反应堆、反应堆50矿50气是正确依赖与造价。没有额外研究或军械库要求。

候选答案：Build a Factory to unlock the Starport. The Starport can build a Reactor for 50 minerals and 50 gas.

## 77/100 sc2qa_000152

原标签：`ambiguous`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** Can a phased Disruptor attack an enemy flying unit?

**原参考答案：** The phased Disruptor can only target ground units. Its weapon deals 145 damage plus 55 bonus damage against shields, but only to ground targets. Therefore it cannot attack flying units unless the target is on the ground.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 需澄清 | complete | ambiguous | medium |
| B | 部分正确 | 需澄清 | missing | ambiguous | medium |
| C | 部分正确 | 需澄清 | not_applicable | ambiguous | medium |

**A 的理由：** 若phased Disruptor指净化新星实体，则爆炸只伤地面，不能伤飞行单位的结论正确；这是技能爆炸并非普通武器攻击，建议将实体名称说清。

未解决项：145加55的附加数值未外部核实；不作版本审计。

候选答案：If “phased Disruptor” means Purification Nova, it damages ground targets only and cannot hit airborne units.

**B 的理由：** 若phased Disruptor指净化新星球，它以到时爆炸伤害地面目标，不是普通武器锁定攻击。不能伤害飞行单位这一结论正确，但应澄清实体并删除‘除非空军在地上’的混乱例外。

未解决项：145加55护盾额外伤害的原始武器字段未提供，未外查数值。

候选答案：If this means the Purification Nova orb, its explosion damages ground units and cannot damage flying units.

**C 的理由：** 若phased Disruptor指净化新星的移动球体，其伤害只作用地面，不能打飞行单位这一结论正确；但它是技能产生的效果而非普通攻击武器，题目实体和攻击用词需澄清。

未解决项：未提供phased Disruptor对应的原始游戏实体，不能完全确认其指代。

候选答案：If this refers to the Purification Nova sphere, it damages ground targets only and cannot damage flying units.

## 78/100 sc2qa_000538

原标签：`multi_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** What is the full building prerequisite chain required to unlock the Terran Thor?

**原参考答案：** The Thor requires an Armory as a building prerequisite. The Armory itself requires a Factory to be constructed first. Therefore, the Factory serves as the foundational building in this prerequisite chain to unlock the Thor.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | multi_hop | high |
| B | 部分正确 | 有效 | missing | multi_hop | high |
| C | 部分正确 | 有效 | missing | multi_hop | high |

**A 的理由：** 工厂→军械库正确，但full chain还需补给站和兵营才能建工厂；雷神需工厂挂科技实验室并有军械库，答案缺实际生产附件。

候选答案：Build Supply Depot → Barracks → Factory, add a Tech Lab to the Factory, and build an Armory. Train the Thor at the Factory with the Tech Lab.

**B 的理由：** 雷神需军械库且军械库需重工厂正确，但题问完整链，遗漏兵营等上游前置和生产雷神所需的重工厂科技实验室。只建工厂和军械库仍未必能造雷神。

候选答案：Build a Supply Depot, Barracks, and Factory. Add a Tech Lab to the Factory and build an Armory; the Factory with its Tech Lab can then produce Thors.

**C 的理由：** 雷神需军械库、军械库需兵工厂这一段正确，但完整链还要兵营解锁兵工厂，且训练雷神的兵工厂必须连接科技实验室。仅有军械库并不足以生产雷神。

候选答案：Build a Barracks, then a Factory. Build an Armory and attach a Tech Lab to the Factory; train the Thor at that Factory.

## 79/100 sc2qa_000156

原标签：`ambiguous`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** What does activating the Infestor's Microbial Shroud require?

**原参考答案：** Microbial Shroud costs 75 energy to activate. The Infestor has a maximum energy of 200. The ability also requires a valid target location within 9 range. Without sufficient energy, the ability cannot be used.

**汇总分流：** 两方未发现答案实质问题，另一方有不同意见。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 部分正确 | 有效 | missing | two_hop | high |

**A 的理由：** 微生物护罩需要能量和范围内合法地点，答案75能量、9施法距离给出实际施放条件；200是最大储能而非费用。

未解决项：9射程未逐项外部核实，不据版本差异判错。

候选答案：The Infestor needs at least 75 energy and a valid target location within cast range.

**B 的理由：** 75能量与9施法距离内合法目标点是微生物菌毯的重要激活要求；答案没有把200能量上限误当消耗，也未编造研究前置。

候选答案：Microbial Shroud requires 75 energy and a valid target point within range 9, while the Infestor is able to cast.

**C 的理由：** 75能量与9范围内有效落点是相关条件；感染虫钻地时不能施放微生物遮蔽，答案应明确需要处于地面可施法状态，200最大能量不能替代此状态限制。

候选答案：An unburrowed Infestor needs at least 75 energy and a valid target location within range 9 to cast Microbial Shroud.

## 80/100 sc2qa_000425

原标签：`single_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** How many minerals does a Robotics Facility cost?

**原参考答案：** The Robotics Facility costs 150 minerals.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 机械台矿价150是可识别的基础造价，所问仅矿石，不必另报气费或完整科技前置。

候选答案：A Robotics Facility costs 150 minerals.

**B 的理由：** 机械台150矿是题目所问的矿物部分，回答没有误用机械研究所或侦察器费用。

候选答案：A Robotics Facility costs 150 minerals.

**C 的理由：** 机械台150矿是可成立的建筑造价；问题只问矿，不要求同时给气体和建造条件。

候选答案：A Robotics Facility costs 150 minerals.

## 81/100 sc2qa_000623

原标签：`single_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** What is the armor value of the Nydus Canal in StarCraft II?

**原参考答案：** The Nydus Canal has an armor value of 1.

**汇总分流：** 两方未发现答案实质问题，另一方有不同意见。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 无法核实 | 需澄清 | uncertain | ambiguous | low |
| B | 未发现实质问题 | 需澄清 | complete | ambiguous | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | medium |

**A 的理由：** Nydus Canal并非通常对战界面的唯一名称，可能指虫洞虫出口或其他虫洞实体；对不同实体直接套1护甲缺少明确映射，不能只凭名称认定。

未解决项：需确认Nydus Canal的具体游戏实体；未提供原始数据映射且未外部核实。

**B 的理由：** 若Nydus Canal对应坑道虫/虫洞出口实体，其基础护甲1符合常见单位数据；名称应明确，避免读者将其与坑道网络建造入口混为一体。

未解决项：英文名称与数据内部实体的精确映射未提供。

候选答案：If Nydus Canal refers to the Nydus Worm exit, it has 1 base armor.

**C 的理由：** Nydus Canal若对应坑道虫/坑道出口，其基础护甲1符合虫族坑道结构数据；答案未混淆为坑道网络生命值。

未解决项：Nydus Canal具体本地化名未随原始实体提供，但所知坑道出口护甲为1。

候选答案：The Nydus Canal has 1 base armor.

## 82/100 sc2qa_000240

原标签：`single_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** How long does it take to produce a Thor in StarCraft II?

**原参考答案：** The production time for a Thor is 43 seconds. This duration is the standard time required to complete the unit's construction.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 雷神43秒对应常见加速游戏时间口径；standard应限定这一口径，不影响单位本身的生产时长回答。

未解决项：未给游戏速度，未外部核实换算。

候选答案：A Thor takes about 43 seconds to train under the usual faster-speed timing convention.

**B 的理由：** 43秒是雷神常用生产时间表述；答案所问为生产时间，没有将军械库或工厂建造耗时合并计算。

未解决项：游戏计时速度口径未明确。

候选答案：A Thor takes 43 seconds to produce in the stated time scale.

**C 的理由：** 雷神43秒生产时间符合常见快速度显示；这是直接时长查询，不需由成本或军械库反推。

候选答案：A Thor takes approximately 43 seconds to train in the stated timing scale.

## 83/100 sc2qa_000293

原标签：`two_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** How does the Medivac's healing ability function in relation to its shield properties?

**原参考答案：** The Medivac possesses a healing ability that is always available and can be set to autocast. This ability allows it to heal a friendly biological unit nearby it, with the constraint that it can only target one unit at a time. Despite having this support capability, the Medivac has no shield points, relying instead on its health for survival.

**汇总分流：** 两方未发现答案实质问题，另一方有不同意见。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 医疗运输机可自动治疗单个友方生物单位且自身无护盾，二者机制正确；但治疗需消耗能量，称always available而不提能量门槛会误导持续治疗能力。

候选答案：A Medivac has no shields. Its autocast Heal restores one nearby friendly biological unit’s health at a time while consuming energy; it cannot restore shields.

**B 的理由：** 医疗运输机能自动治疗附近友方生物单位、一次一个目标，自身没有护盾，答案没有把治疗能力误解释为自带护盾。‘始终可用’宜理解为无需研究，并非治疗不耗能量。

候选答案：A Medivac can autocast healing on one nearby friendly biological unit at a time, using energy to restore health. The Medivac itself has no shields.

**C 的理由：** 医疗运输机可自动治疗附近友方生物单位且一次一个目标，自身没有护盾；治疗能力与自身无护盾并不冲突。always available宜理解为默认拥有该技能。

候选答案：A Medivac uses energy to heal one nearby friendly biological unit at a time and can autocast Heal. It has no shields.

## 84/100 sc2qa_000292

原标签：`two_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** How does the Chrono Boost ability function in relation to the Nexus, and what is its armor value?

**原参考答案：** Chrono Boost is an ability available on the Nexus that increases the production speed of a structure by 50% for 20 seconds, costing 25 energy. The Nexus itself has a survival armor value of 1.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | medium |

**A 的理由：** 时空加速来源星灵枢纽、提高建筑生产速度50%及枢纽基础护甲1合理；25能量和20秒是一组可识别的时空加速数据，不因版本差异判错。

未解决项：25能量、20秒未逐项外部核实；本次不作版本审计。

候选答案：Chrono Boost is cast by the Nexus on a friendly production or research structure to increase its work rate. The Nexus has 1 base armor.

**B 的理由：** 时空加速归属星灵枢纽、提高建筑生产速度，枢纽基础护甲1均正确；25能量/20秒/50%作为给定技能参数未发现内部语义冲突，不据参数口径做版本审计。

未解决项：具体25能量、20秒与50%未取得外部原始数据逐项核验。

候选答案：Chrono Boost is cast by the Nexus on a structure to speed its production. The Nexus has 1 base armor.

**C 的理由：** 星空加速属于星灵枢纽技能，提高建筑工作速率50%、持续20秒、25能量这一数据组合成立；枢纽基础护甲1也正确。两项是并列属性，不产生因果关系。

未解决项：未提供目标建筑限制及时间标尺原始数据；不据其他参数组合审计版本。

候选答案：Chrono Boost is a Nexus ability that increases a target structure's work rate by 50% for 20 game-time seconds at a cost of 25 energy in this data scale. A Nexus has 1 base armor.

## 85/100 sc2qa_000850

原标签：`single_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** How long does it take to build an Evolution Chamber?

**原参考答案：** The Evolution Chamber takes 25 seconds to build.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | medium |

**A 的理由：** 进化腔25秒为基础建造时间表达，问题为直接属性查询，答案包含秒数单位。

未解决项：未说明游戏速度口径，不据此判为事实错误。

候选答案：An Evolution Chamber takes 25 seconds to build in the base-time convention.

**B 的理由：** 25秒是进化腔常见基础建造时间；答案给出秒单位并直接回应所问，没有混淆升级研究时长。

未解决项：实际游戏速度下秒数换算口径未说明。

候选答案：An Evolution Chamber takes 25 game seconds to build in the stated time scale.

**C 的理由：** 进化腔建造25游戏秒与常用Normal时间值一致；问题单问时长，不需要引入升级研究时间。

未解决项：游戏速度与现实时间换算未给出。

候选答案：An Evolution Chamber takes 25 game-time seconds to build in this timing scale.

## 86/100 sc2qa_000742

原标签：`multi_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** What building prerequisites must be met before a Protoss Disruptor can be produced?

**原参考答案：** The Disruptor requires a Cybernetics Core to be built first. The Cybernetics Core in turn requires a Gateway. Therefore, the building prerequisite chain is Gateway → Cybernetics Core → Disruptor.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 有效 | missing | multi_hop | high |
| C | 存在错误 | 有效 | missing | multi_hop | high |

**A 的理由：** 传送门到控制芯核正确，但干扰者必须由机械台在有机械研究所时生产；答案把前期科技直接连接到干扰者，漏两个关键建筑。

候选答案：Build a Gateway, Cybernetics Core, Robotics Facility, and Robotics Bay with Pylon power. Produce Disruptors at the Robotics Facility.

**B 的理由：** 网关—控制核心只是干扰者科技链前段；还必须建机械台作为生产建筑、机械研究所作为解锁建筑。控制核心不能直接产干扰者。

候选答案：Build a Gateway, Cybernetics Core, Robotics Facility, and Robotics Bay. Disruptors are produced at the Robotics Facility.

**C 的理由：** 干扰者的生产建筑机械台和最终科技机械研究所都被遗漏；兵营—控制核心之后不能直接生产干扰者，这一链缺少两个必要节点。

候选答案：Gateway → Cybernetics Core → Robotics Facility → Robotics Bay. Train the Disruptor at the Robotics Facility.

## 87/100 sc2qa_000598

原标签：`ambiguous`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** Can an Orbital Command drop a MULE anywhere at any time?

**原参考答案：** An Orbital Command cannot drop a MULE anywhere at any time due to specific activation requirements. The ability costs 50 energy to cast, so it cannot be used if the structure lacks sufficient energy. Additionally, the ability may only be targeted on areas that are uncovered by the fog of war. Since the Orbital Command can store up to 200 energy, it has the capacity to cast multiple MULEs when these conditions are met.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | complete | two_hop | high |

**A 的理由：** 空投矿骡50能量且要求目标区域有当前视野，不能任意无视迷雾施放；200能量可支持多次使用这一推断没有超出这些条件。

候选答案：No. Calldown: MULE requires 50 energy and a valid target location in an area with vision.

**B 的理由：** 矿骡需50能量且需要对目标落点有视野，答案正面否定任意时间任意地点召唤。200能量只支持多次施放，并未被当作一次费用。

候选答案：Call Down MULE costs 50 energy and requires a valid visible landing location; it cannot be cast anywhere at any time.

**C 的理由：** 矿骡投放需50能量且落点要在当前视野内，是对anywhere at any time的正确限制；200能量上限仅说明储能上限，不等同无限连续投放。

候选答案：No. Call Down MULE requires 50 energy and a valid ground landing location with current vision.

## 88/100 sc2qa_000875

原标签：`two_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** Can the Terran Starport create a Reactor, and does it have a shield to protect itself?

**原参考答案：** The Terran Starport is always able to create a Reactor as one of its abilities. However, the Starport possesses a shield attribute of zero, meaning it lacks any shield protection.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | single_hop | high |
| B | 部分正确 | 有效 | missing | single_hop | high |
| C | 部分正确 | 有效 | missing | single_hop | high |

**A 的理由：** 星港无护盾正确，也确有建反应堆能力；但always able过强，需着陆、无现有附件、右侧空间可用及50矿50气，不能无条件创建。

候选答案：A grounded Starport can build a Reactor if it has no add-on, has clear add-on space, and you can pay 50 minerals and 50 gas. It has 0 shields.

**B 的理由：** 星港能建反应堆且自身无护盾正确，但‘always able’省略落地、空闲附加建筑位及50矿50气等条件。已有科技实验室或被阻挡时不能直接再建反应堆。

候选答案：A Starport has no shields. It can build a Reactor while landed with a free, unobstructed add-on space and 50 minerals plus 50 gas available.

**C 的理由：** 星港能建反应堆且没有护盾正确；但always able不准确，星港需着陆、附属建筑槽位与旁边空间可用，并支付50矿50气，已有附属建筑时不能再直接建一个。

候选答案：A Starport can build a Reactor when landed with an available add-on position and sufficient resources. It has no shields.

## 89/100 sc2qa_000639

原标签：`single_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** How much supply does the Ghost Academy require to build?

**原参考答案：** The Ghost Academy requires 0 supply to build.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | not_applicable | single_hop | high |
| B | 未发现实质问题 | 有效 | complete | single_hop | high |
| C | 未发现实质问题 | 有效 | not_applicable | single_hop | high |

**A 的理由：** 幽灵学院是建筑，建造不占人口；不能与幽灵单位训练的人口费用混淆。

候选答案：A Ghost Academy costs 0 supply to build.

**B 的理由：** 幽灵军校是建筑，不占人口，0人口回答准确；资源和科技前置不应与人口成本混淆。

候选答案：A Ghost Academy requires 0 supply.

**C 的理由：** 幽灵学院是建筑，不消耗人口；答案0人口直接准确，没有把幽灵单位的人口当成学院成本。

候选答案：A Ghost Academy requires 0 supply.

## 90/100 sc2qa_000122

原标签：`multi_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** Which buildings must be constructed before you can build a Carrier?

**原参考答案：** To build a Carrier, you must first have a Stargate. The Stargate, in turn, requires a Gateway. Thus, the Gateway is the initial structure needed in this tech chain.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 有效 | missing | multi_hop | high |
| C | 存在错误 | 有效 | missing | multi_hop | high |

**A 的理由：** 航母由星门生产但还需舰队航标；星门直接需控制芯核而非仅传送门。答案给出的链无法实际解锁航母。

候选答案：Build a Gateway, Cybernetics Core, Stargate, and Fleet Beacon with Pylon power. Train the Carrier at the Stargate.

**B 的理由：** 航母除星门外还必须有舰队航标；星门的直接前置为控制核心而非网关。答案两处省略导致不可执行的航母科技链。

候选答案：Build a Gateway, Cybernetics Core, Stargate, and Fleet Beacon; train the Carrier at the Stargate.

**C 的理由：** 航母需要舰队航标这一最终科技，星门还需控制核心；答案漏两项核心建筑且把星门直接前置写为兵营，流程不可执行。

候选答案：Build a Gateway, Cybernetics Core, Stargate and Fleet Beacon. Produce the Carrier at the Stargate.

## 91/100 sc2qa_000768

原标签：`ambiguous`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** If the enemy unit’s ground‑or‑air status is unknown, can a Zealot still attack it?

**原参考答案：** The Zealot’s weapon is set to target ground units only, so it can only engage ground targets. It cannot attack air units. Therefore, whether the Zealot can hit the enemy depends on the enemy being a ground unit.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 需澄清 | complete | ambiguous | high |
| B | 未发现实质问题 | 需澄清 | complete | ambiguous | high |
| C | 未发现实质问题 | 需澄清 | complete | ambiguous | high |

**A 的理由：** 狂热者只能攻击地面，目标层未知时不能保证可攻击；答案正确回答条件而没有把近战范围当成空中可达性。

候选答案：A Zealot can attack only ground targets, so clarify the enemy’s ground-or-air status.

**B 的理由：** 狂热者普通近战攻击只能对地，目标层未给定时只能给条件判断；答案对此准确，没有将冲锋机动性误当对空能力。

候选答案：A Zealot can attack ground units only, so the enemy's layer must be known before confirming it can engage.

**C 的理由：** 狂热者近战只能攻击地面；答案在目标层级未知时保留地面目标这一必要条件，正确处理题目缺失信息。

候选答案：A Zealot can attack only ground targets. The target's layer must be known to decide whether it can engage.

## 92/100 sc2qa_000735

原标签：`multi_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** What is the cost of a Warp Prism, and which building must be built before the Robotics Facility required to produce it?

**原参考答案：** The Warp Prism costs 250 minerals, 2 supply, and takes 50 seconds to build, and it is produced from a Robotics Facility. The Robotics Facility can only be constructed after a Gateway has been built. The Gateway is a Protoss building that serves as the prerequisite for the Robotics Facility.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | two_hop | high |
| B | 存在错误 | 有效 | missing | two_hop | high |
| C | 部分正确 | 有效 | missing | multi_hop | high |

**A 的理由：** 折跃棱镜250矿2人口、机械台生产正确；机械台的直接前置是控制芯核，答案将传送门这个间接前置当成充分条件。

未解决项：附加50秒建造时间未核实计时口径。

候选答案：A Warp Prism costs 250 minerals and 2 supply and is produced at a Robotics Facility. A Cybernetics Core must be built to unlock that Facility; the Core itself requires a Gateway.

**B 的理由：** 棱镜250矿2人口与机械台生产关系正确；机械台直接前置是控制核心，答案将网关写成直接前置并漏控制核心，会使建筑链不完整。

未解决项：附加50秒生产时间的口径未独立核验。

候选答案：A Warp Prism costs 250 minerals, no gas, and 2 supply. Build a Cybernetics Core before the Robotics Facility; the Core itself requires a Gateway.

**C 的理由：** 折跃棱镜250矿2人口与机械台生产可成立；机械台直接科技前置是控制核心，答案只列兵营并把它当直接前置，省略了必要中间建筑。

候选答案：A Warp Prism costs 250 minerals and 2 supply. It is produced at a Robotics Facility, which requires a Cybernetics Core; the Core requires a Gateway.

## 93/100 sc2qa_000559

原标签：`ambiguous`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** Can a Nydus Network summon a Nydus Worm at any location on the map?

**原参考答案：** A Nydus Network can only create a Nydus Worm at a point that is visible to the player, so locations without vision cannot be targeted. The summoning also requires 75 minerals and 75 gas to activate. Additionally, the ability has a 14-second cooldown that must elapse before another Nydus Worm can be created.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | single_hop | medium |
| B | 部分正确 | 有效 | missing | single_hop | high |
| C | 部分正确 | 有效 | missing | two_hop | high |

**A 的理由：** 需要视野、矿气及冷却的描述正确方向，但有视野并不意味着任意地形都能放虫洞虫，还需合法可放置区域与空间。

未解决项：14秒冷却尚未外部核实时间口径。

候选答案：No. A Nydus Worm requires a visible, valid placement location, sufficient resources, and a ready cooldown; it cannot be placed on arbitrary terrain.

**B 的理由：** 可见落点、75矿75气与冷却限制说明正确方向；但坑道虫还要求合法可放置的地面空间，不能在可见水域、不可建地形或被阻挡处任意召唤。题问地图任意位置，应补该条件。

未解决项：14秒冷却的精确取整与计时口径未外查。

候选答案：A Nydus Worm requires a visible, valid, unobstructed placement location, 75 minerals and 75 gas, and the summon ability to be ready.

**C 的理由：** 视野、75矿75气和14秒冷却均正确，后两项有实际访问的暴雪页支持；但可见并不保证能召唤，坑道虫还需合法可放置的地面位置，不能放在悬崖空域或被占据的地块。

候选答案：No. A Nydus Worm needs a visible, valid ground placement location, 75 minerals and 75 gas, and the summoning ability must be off cooldown.

查阅来源：[1](https://news.blizzard.com/en-us/article/23227811/starcraft-ii-4-11-0-patch-notes)

## 94/100 sc2qa_000118

原标签：`multi_hop`；生成模型：`deepseek-ai/DeepSeek-V4-Flash`。

**问题：** What buildings must be constructed to eventually produce an Archon?

**原参考答案：** An Archon requires a Warp Gate as a prerequisite building. A Warp Gate requires a Cybernetics Core as a prerequisite building. The Cybernetics Core is a Protoss building.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 有效 | missing | multi_hop | high |
| C | 存在错误 | 有效 | missing | multi_hop | high |

**A 的理由：** 执政官不是从折跃门直接生产的，折跃门也并非必需，可用普通传送门生产圣堂再合体；答案漏暮光议会及圣堂文库或黑暗圣坛。

候选答案：Build Gateway → Cybernetics Core → Twilight Council, then Templar Archives or Dark Shrine. Produce two High and/or Dark Templar and merge them into an Archon; Warp Gate is optional.

**B 的理由：** 折跃门并非执政官必要前置，普通网关也能生产用于合体的圣堂武士。真正缺失的是暮光议会之后的圣堂文献馆或黑暗圣坛，以及两名圣堂武士合体。

候选答案：Build a Gateway, Cybernetics Core, Twilight Council, and either Templar Archives or a Dark Shrine. Produce two High Templar and/or Dark Templar and merge them. Warp Gate is optional.

**C 的理由：** 执政官由两名圣堂武士融合而成，普通兵营也能训练圣堂武士，因此折跃门不是必需建筑。答案同时漏暮光议会和圣堂文库/黑暗圣坛科技，不能支持融合执政官。

候选答案：Build a Gateway, Cybernetics Core and Twilight Council, then Templar Archives or a Dark Shrine to obtain Templars. Merge any two High/Dark Templars into an Archon.

## 95/100 sc2qa_000295

原标签：`two_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** What is the energy cost and duration of the Mothership Core's Time Warp ability, and what is its survival shield value?

**原参考答案：** The Mothership Core's Time Warp ability costs 75 energy and creates a field that lasts for 30 seconds. This ability slows the movement speed of ground units in the affected area by 50%. Additionally, the Mothership Core possesses a survival shield with a value of 60.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | single_hop | medium |
| B | 未发现实质问题 | 有效 | complete | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | medium |

**A 的理由：** 母舰核心护盾60、时空扭曲75能量和减慢区域地面单位50%均为可识别机制；30秒持续对应一种数据口径，不作版本审计。

未解决项：附加持续30秒未用原始数据外部核实。

候选答案：In the stated data, Time Warp costs 75 energy, lasts 30 seconds, and slows affected ground units by 50%. The Mothership Core has 60 shields.

**B 的理由：** 母舰核心60护盾、时间扭曲75能量以及影响地面移动速度的区域减速效果符合其技能描述；所列30秒参数不构成内部矛盾，不以版本作否定理由。

未解决项：精确持续时间与百分比未取得外部原始数据逐项认证。

候选答案：Time Warp costs 75 energy and creates a 30-second field slowing affected ground units by 50%. The Mothership Core has 60 shields.

**C 的理由：** 母舰核心时间扭曲75能量、30游戏秒场及地面单位减速50%与其60护盾是可成立的数据组合；问题两项属性并列，不需从技能效果推导护盾。

未解决项：未提供原始技能数据与时间标尺；未进行版本比较。

候选答案：Time Warp costs 75 energy and creates a 30-game-second field that slows ground units by 50% in this data scale. The Mothership Core has 60 shields.

## 96/100 sc2qa_000745

原标签：`multi_hop`；生成模型：`MiniMaxAI/MiniMax-M2.5`。

**问题：** What buildings must a Protoss player have constructed before they can morph an Archon?

**原参考答案：** An Archon requires a Twilight Council to be built. The Twilight Council itself requires a Cybernetics Core to be constructed first. Therefore, a Cybernetics Core is the foundational building needed to eventually morph an Archon.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 有效 | missing | multi_hop | high |
| C | 部分正确 | 有效 | missing | multi_hop | high |

**A 的理由：** 暮光议会及控制芯核是上游必要科技，但还需圣堂文库或黑暗圣坛来获得两名圣堂单位；有暮光议会本身不提供合体素材。

候选答案：Build a Gateway, Cybernetics Core, Twilight Council, and either Templar Archives or Dark Shrine. Produce two eligible Templar and merge them into an Archon.

**B 的理由：** 控制核心—暮光议会是正确的上游关系，但建到暮光议会仍不能合执政官；还需要文献馆或黑暗圣坛以获得两名高阶/黑暗圣堂武士，答案未给出必要的最终解锁。

候选答案：Build a Gateway, Cybernetics Core, Twilight Council, and either Templar Archives or a Dark Shrine; obtain two High Templar and/or Dark Templar and merge them into an Archon.

**C 的理由：** 暮光议会需控制核心这段关系正确，但仅有两者不能得到可融合单位；还需圣堂文库出高阶圣堂或黑暗圣坛出黑暗圣堂，并由两名圣堂融合。

候选答案：Build a Gateway, Cybernetics Core and Twilight Council, then Templar Archives or a Dark Shrine. Produce two eligible Templars and merge them into an Archon.

## 97/100 sc2qa_000815

原标签：`single_hop`；生成模型：`zai-org/GLM-5.2`。

**问题：** What is the production time of a Barracks?

**原参考答案：** The production time for a Barracks is 46.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | uncertain | single_hop | medium |
| B | 部分正确 | 有效 | missing | single_hop | medium |
| C | 未发现实质问题 | 有效 | complete | single_hop | high |

**A 的理由：** 46可对应兵营常见加速时间建造时长，但原答案连秒数单位都没有；应补单位和计时口径，不能仅凭裸数字完整作答。

未解决项：未外部核实46的速度换算。

候选答案：A Barracks takes about 46 seconds to build under the usual faster-speed timing convention.

**B 的理由：** 46可对应兵营常见建造秒数，但答案是裸数，无单位和计时口径；应明确是建造时间而非生产部队时间。

未解决项：46的游戏时间/实际时间单位未提供。

候选答案：A Barracks takes 46 seconds to build in the stated time scale.

**C 的理由：** 兵营约46秒建造时间符合常用快速度口径；答案漏写秒但数值能对应明确的建造时长，不应把单位缺省直接判作事实错误。

未解决项：答案应补上秒并在数据集统一声明计时口径。

候选答案：A Barracks takes approximately 46 seconds to build in this timing scale.

## 98/100 sc2qa_000294

原标签：`two_hop`；生成模型：`Qwen/Qwen3.6-35B-A3B`。

**问题：** What is the health of the Baneling unit that has the ability to automatically target structures?

**原参考答案：** The Baneling is a Zerg unit that possesses the Enable Attack Building ability, which allows it to automatically target enemy structures. This specific unit has a survival health value of 30.

**汇总分流：** 三方均未发现答案实质问题。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 未发现实质问题 | 有效 | complete | two_hop | high |
| B | 未发现实质问题 | 有效 | complete | two_hop | high |
| C | 未发现实质问题 | 有效 | complete | two_hop | high |

**A 的理由：** 启用攻击建筑是毒爆可自动寻敌建筑的开关，单位仍是毒爆；其基础生命30符合所问，没有把开关误当增加生命的效果。

候选答案：A Baneling has 30 base health. Enable Attack Building lets it automatically acquire structures as targets.

**B 的理由：** 爆虫具有攻击建筑自动目标开关，基础生命30与所问属性一致。此处是先按能力识别单位再读取生命，不应因为能力名中有Building就把它当建筑。

候选答案：A Baneling has 30 base health. Enable Attack Building allows automatic attacks on structures.

**C 的理由：** 允许攻击建筑切换命令属于爆虫，爆虫基础生命30正确；这里先由技能识别单位，再查其生命值，是两步属性关联。

候选答案：The Baneling has 30 base health.

## 99/100 sc2qa_000474

原标签：`two_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** What are the resource costs to produce a Ravager from a Roach, and what effects does its Corrosive Bile ability have?

**原参考答案：** The Ravager costs 25 minerals, 75 gas, and 3 supply to produce from a Roach. Its Corrosive Bile ability launches a glob of bile that descends on a target point after 2 seconds, dealing 60 damage to enemies in an area of effect. This ability hits both air and ground units, destroys force fields, and has a range of 9 with a 7-second cooldown.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 部分正确 | 有效 | missing | single_hop | high |
| B | 部分正确 | 有效 | missing | single_hop | high |
| C | 部分正确 | 需澄清 | missing | two_hop | high |

**A 的理由：** 25矿75气是变异增量费用，3人口是破坏者总占用，变异只额外需1人口；腐蚀胆汁还会误伤友军而非只对敌人结算，答案遗漏此效果限制。

未解决项：2秒延迟、9射程和7秒冷却未逐项外部核实，不作版本审计。

候选答案：Morphing a Roach into a Ravager costs 25 minerals, 75 gas, and 1 additional supply, for 3 total supply. Corrosive Bile deals 60 area damage to ground and air units, can hit friendly units, and destroys Force Fields after its landing delay.

**B 的理由：** 25矿75气是蟑螂变破坏者的增量资源费，但3人口是成品总占用，变形只多需1人口。胆汁60伤害、可对空对地并破力场正确，但并非只伤敌人，也可能伤及友军。

未解决项：2秒落点延迟及7秒冷却的计时口径未外查。

候选答案：Morphing a Roach into a Ravager costs 25 minerals, 75 gas, and 1 additional supply (3 total). Corrosive Bile deals 60 area damage to ground and air units, can cause friendly fire, and destroys Force Fields.

**C 的理由：** 25矿75气为蟑螂变破坏者增量，但3是成品总人口，变形只额外用1人口；把增量资源与总人口并列称成本应说明。胆汁60伤害空地、破力场正确，但也会伤及友军，不能只描述敌军伤害而漏掉关键误伤机制。

未解决项：题中延迟2秒及冷却7秒按其计时口径理解，未外查精度。

候选答案：Morphing a Roach into a Ravager costs 25 minerals, 75 gas and 1 additional supply (3 total). Corrosive Bile deals 60 area damage after a delay, hits ground and air units including friendly units, and destroys Force Fields.

## 100/100 sc2qa_000518

原标签：`multi_hop`；生成模型：`Pro/zai-org/GLM-5.1`。

**问题：** What is the building prerequisite chain required to unlock the High Templar?

**原参考答案：** The High Templar requires a Twilight Council as a building prerequisite. In turn, the Twilight Council requires a Gateway to be constructed. The Gateway is a Protoss building that forms the base of this prerequisite chain.

**汇总分流：** 至少两方认为答案部分正确或存在错误。

| 审核者 | 答案判断 | 问题判断 | 条件 | 盲推断题型 | 置信度 |
|---|---|---|---|---|---|
| A | 存在错误 | 有效 | missing | multi_hop | high |
| B | 存在错误 | 有效 | missing | multi_hop | high |
| C | 存在错误 | 有效 | missing | multi_hop | high |

**A 的理由：** 高阶圣堂武士直接科技前置是圣堂文库而非暮光议会；暮光议会直接需控制芯核而非仅传送门，答案漏两处关键建筑。

候选答案：Build a powered Gateway, Cybernetics Core, Twilight Council, and Templar Archives. Train High Templar at a Gateway or warp them in from a Warp Gate.

**B 的理由：** 高阶圣堂武士的最终解锁建筑是圣堂文献馆；暮光议会的直接前置是控制核心，答案遗漏核心与文献馆两项必需建筑。

候选答案：Build a Gateway, Cybernetics Core, Twilight Council, and Templar Archives; train High Templar at a Gateway or warp them in with a Warp Gate.

**C 的理由：** 高阶圣堂最终科技前置是圣堂文库；暮光议会直接前置是控制核心。答案漏掉控制核心与圣堂文库并把兵营接暮光议会，不能解锁高阶圣堂。

候选答案：Build a Gateway, Cybernetics Core, Twilight Council and Templar Archives. Train a High Templar at a Gateway or warp one in at a Warp Gate.

**玩家补充核查：** 高阶圣堂科技链遗漏圣堂文库，并将暮光议会前置直接写成传送门（Gateway）。 GATEWAY→HIGHTEMPLAR 要求 TEMPLARARCHIVE；TEMPLARARCHIVE 要求 TWILIGHTCOUNCIL；TWILIGHTCOUNCIL 要求 CYBERNETICSCORE。 外部来源支持两项关系问题。

来源：[S1](https://raw.githubusercontent.com/BurnySc2/python-sc2/develop/sc2/dicts/unit_train_build_abilities.py)

关系修正候选：The technology path includes Gateway, Cybernetics Core, Twilight Council, and Templar Archives. High Templar are trained at a Gateway or warped in through an available Warp Gate after the Templar Archives requirement is met.
