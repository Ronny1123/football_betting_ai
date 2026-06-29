# Football Betting AI

策略引擎 V2：手动输入比赛概率和赔率，生成任选九场的推荐组合。

## 运行

```bash
python3 src/main.py
```

程序会读取：

```text
data/matches.csv
```

并输出：

```text
output/recommendations.csv
```

## 数据字段

`matches.csv` 每行代表一场比赛：

```text
match_id,home,away,p3,p1,p0,odds3,odds1,odds0,manual_lock,manual_exclude
```

- `p3`: 主胜概率
- `p1`: 平局概率
- `p0`: 主负概率
- `odds3`: 主胜赔率
- `odds1`: 平局赔率
- `odds0`: 主负赔率
- `manual_lock`: 手动锁定结果，可填 `3`、`1`、`0`
- `manual_exclude`: 是否排除，`1` 表示排除

## 参数

常用参数在 `src/config.py`：

```python
TARGET_HITS = 9
TOP_N = 20
AUTO_LOCK_ENABLED = True
AUTO_LOCK_THRESHOLD = 0.90
RANK_MODE = "probability"
```

`RANK_MODE` 支持：

- `probability`: 按组合命中概率排序
- `ev`: 按组合期望收益排序

单场 EV：

```text
EV = 概率 * 赔率
```
