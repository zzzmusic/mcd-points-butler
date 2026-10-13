#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麦麦积分管家 —— 积分价值最大化计算器（辅助脚本）

读取麦当劳 MCP 工具返回的 JSON，给出：
  1) 即将过期积分的紧急度与建议处理时限
  2) 麦麦商城兑换的「每积分性价比」排序
  3) 积分抽奖的期望价值（EV）估算与风险提示
  4) 一句总建议（换商城 / 抽奖 / 先留着）

设计为防御式：字段缺失时降级为定性提示，绝不抛异常中断。
所有数值仅为基于官方实时数据的估算，最终以麦当劳官方渠道为准。
"""

import argparse
import json
import sys
from datetime import datetime, date


def _load(text):
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        return {}


def parse_expire(dt_str):
    """尽力解析过期时间，返回 datetime 或 None。"""
    if not dt_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(str(dt_str).strip(), fmt)
        except Exception:
            continue
    return None


def account_summary(account):
    out = {}
    # 兼容多种可能的字段名
    avail = account.get("availablePoints") or account.get("available_points") \
        or account.get("points") or account.get("availablePoints") or 0
    expiring = account.get("expiringPoints") or account.get("expiring_points") \
        or account.get("willExpirePoints") or 0
    expire_at = account.get("expireDate") or account.get("expire_date") \
        or account.get("expiringDate") or account.get("expireAt") or None
    out["available"] = _to_int(avail)
    out["expiring"] = _to_int(expiring)
    out["expire_at"] = expire_at
    return out


def _to_int(v):
    try:
        return int(float(v))
    except Exception:
        return 0


def expire_urgency(a_summary):
    """返回 (level, msg)。level: high/mid/low/none"""
    expiring = a_summary.get("expiring", 0)
    if expiring <= 0:
        return "none", "暂无即将过期的积分，可从容规划。"
    d = parse_expire(a_summary.get("expire_at"))
    if d is None:
        return "mid", f"有 {expiring} 分即将过期（未解析到具体日期），建议尽快使用。"
    days = (d.date() - date.today()).days
    if days < 0:
        return "high", f"有 {expiring} 分已在 {d.date()} 过期，建议立即核查账户。"
    if days <= 7:
        return "high", f"有 {expiring} 分将于 {d.date()} 过期（剩 {days} 天），优先级最高，建议先花掉。"
    if days <= 30:
        return "mid", f"有 {expiring} 分将于 {d.date()} 过期（剩 {days} 天），可在本月内安排使用。"
    return "low", f"有 {expiring} 分将于 {d.date()} 过期（剩 {days} 天），时间充裕。"


def mall_ranking(mall):
    """商城兑换性价比排序。有参考现金价则按 现金/积分；否则按类型标注。"""
    items = []
    # mall-points-products 可能直接是 list，或包在 {products:[...]} / {items:[...]}
    if isinstance(mall, list):
        raw = mall
    else:
        raw = mall.get("products") or mall.get("items") or mall.get("list") or []
    for it in raw:
        name = it.get("name") or it.get("title") or it.get("productName") or "未命名商品"
        cost = _to_int(it.get("points") or it.get("pointCost") or it.get("cost") or 0)
        cash = _to_float(it.get("cashValue") or it.get("referencePrice")
                        or it.get("price") or it.get("cash"))
        kind = it.get("type") or it.get("category") or "未知类型"
        if cost <= 0:
            continue
        if cash:
            ratio = cash / cost  # 每 1 积分 ≈ ratio 元
            items.append((name, cost, kind, round(ratio, 4), f"≈¥{cash}/ {cost}分 (每分¥{ratio:.3f})"))
        else:
            items.append((name, cost, kind, None, f"{cost}分/{kind}（无参考现金价）"))
    # 有 ratio 的按性价比降序
    items.sort(key=lambda x: (x[3] is not None, x[3] if x[3] is not None else 0), reverse=True)
    return items


def _to_float(v):
    try:
        return float(v)
    except Exception:
        return None


def lottery_ev(lottery, available):
    """抽奖期望价值估算。需要奖品价值与概率；缺失则定性提示。"""
    if not lottery:
        return None, "未获取到抽奖活动信息（query-lottery-info 为空）。"
    status = lottery.get("status") or lottery.get("activityStatus") or ""
    cost = _to_int(lottery.get("costPerDraw") or lottery.get("drawCost")
                   or lottery.get("consumePoints") or 0)
    prizes = lottery.get("prizes") or lottery.get("prizeList") or []
    if status and str(status) not in ("进行中", "active", "1", "open", ""):
        return None, f"当前抽奖活动状态：{status}，可能未开启。"
    if cost <= 0:
        return None, "未解析到单次抽奖消耗积分，无法估算 EV；请核对 query-lottery-info 返回。"
    # 若有奖品价值与概率则算 EV
    ev = 0.0
    has_prob = False
    detail = []
    for p in prizes:
        val = _to_float(p.get("value") or p.get("cashValue") or p.get("price")) or 0
        prob = _to_float(p.get("probability") or p.get("rate") or p.get("chance"))
        if prob is not None:
            has_prob = True
            ev += val * prob
            detail.append(f"{p.get('name','奖品')}: 价值¥{val} × 概率{prob}")
    if has_prob:
        # 仅作粗略参照：以「100 积分 ≈ ¥1」折算单次消耗，便于和 EV 直观对照（非精确财务结论）
        cost_yuan_ref = cost / 100.0
        cmp_word = ("高于" if ev > cost_yuan_ref else ("约等于" if abs(ev - cost_yuan_ref) < 0.01 else "低于"))
        verdict = ("抽奖单次期望价值约 ¥%.2f，单次消耗 %d 分（粗略折算≈¥%.2f）。EV%s该折算值，"
                   "属博彩性质，请理性参与。" % (ev, cost, cost_yuan_ref, cmp_word))
        return ev, verdict + ("；明细：" + "；".join(detail) if detail else "")
    return None, (f"单次消耗 {cost} 分，但奖品概率未公开，无法精确估算 EV；"
                  f"抽奖具概率性，建议仅在积分充裕/即将过期且想碰运气时参与。")


def recommend(a_summary, mall_items, lottery_verdict, urgency):
    avail = a_summary.get("available", 0)
    expiring = a_summary.get("expiring", 0)
    if expiring > 0 and mall_items:
        best = mall_items[0]
        return (f"建议优先把即将过期的 {expiring} 分拿去换「{best[0]}」"
                f"（{best[4]}），避免清零；剩余积分再考虑抽奖或攒着。")
    if urgency == "none" and mall_items:
        return "当前无过期压力，可对比商城兑换与抽奖后从容决定；稳妥优先选高性价比商城商品。"
    if not mall_items and lottery_verdict:
        return "未获取到商城商品，建议以抽奖/保留为主，或稍后重试 mall-points-products。"
    return "建议先查全账户与商城数据后再决策。"


def main():
    ap = argparse.ArgumentParser(description="麦麦积分管家 - 积分价值最大化计算器")
    ap.add_argument("--account", help="query-my-account 的 JSON")
    ap.add_argument("--mall", help="mall-points-products 的 JSON")
    ap.add_argument("--lottery", help="query-lottery-info 的 JSON")
    args = ap.parse_args()

    account = _load(args.account)
    mall = _load(args.mall)
    lottery = _load(args.lottery)

    a = account_summary(account)
    urg_level, urg_msg = expire_urgency(a)
    mall_items = mall_ranking(mall)
    ev, lot_msg = lottery_ev(lottery, a.get("available", 0))
    rec = recommend(a, mall_items, lot_msg, urg_level)

    print("=" * 48)
    print("麦麦积分管家 · 积分价值测算")
    print("=" * 48)
    print(f"[积分总览] 可用 {a['available']} 分，即将过期 {a['expiring']} 分"
          + (f"（过期日 {a['expire_at']}）" if a['expire_at'] else ""))
    print(f"[紧急度:{urg_level}] {urg_msg}")
    print("-" * 48)
    print("[商城兑换性价比]")
    if mall_items:
        for i, (name, cost, kind, ratio, line) in enumerate(mall_items[:10], 1):
            print(f"  {i}. {name} | {line}")
    else:
        print("  （未获取到商城商品列表）")
    print("-" * 48)
    print("[积分抽奖]")
    print("  " + lot_msg)
    print("-" * 48)
    print("[总建议] " + rec)
    print("=" * 48)
    print("注：以上为基于官方实时数据的估算，最终以麦当劳官方渠道为准。")


if __name__ == "__main__":
    main()
