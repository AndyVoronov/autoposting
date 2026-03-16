import re
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.censorship import CensorshipRule, CensorshipLog
from app.services.ai import ai_service


class CensorshipService:
    DEFAULT_BANNED_WORDS = [
        "протест",
        "митинг",
        "оппозиция",
        "навальный",
        "путин должен уйти",
        "война в украине",
        "специальная операция провалилась",
        "санкции против россии",
        "кремль",
        "президент сбежал",
        "государственный переворот",
        "революция",
        "свержение",
    ]

    DEFAULT_WARN_WORDS = [
        "политика",
        "выборы",
        "кризис",
        "инфляция",
        "коррупция",
        "экономические проблемы",
        "бедность",
        "безработица",
    ]

    def __init__(self, db: AsyncSession):
        self.db = db
        self._rules_cache: Optional[list[CensorshipRule]] = None

    async def get_rules(self) -> list[CensorshipRule]:
        if self._rules_cache is None:
            result = await self.db.execute(
                select(CensorshipRule).where(CensorshipRule.is_active == True)
            )
            self._rules_cache = result.scalars().all()
        return self._rules_cache

    def clear_cache(self):
        self._rules_cache = None

    async def check_text(self, text: str, post_id: Optional[int] = None) -> dict:
        result = {
            "passed": True,
            "action": "allow",
            "matched_rules": [],
            "ai_check": None,
        }

        text_lower = text.lower()

        # Check banned words from default list
        for word in self.DEFAULT_BANNED_WORDS:
            if word.lower() in text_lower:
                result["passed"] = False
                result["action"] = "reject"
                result["matched_rules"].append(
                    {
                        "pattern": word,
                        "type": "banned",
                        "source": "default",
                    }
                )

        # Check warn words
        for word in self.DEFAULT_WARN_WORDS:
            if word.lower() in text_lower:
                result["action"] = "warn"
                result["matched_rules"].append(
                    {
                        "pattern": word,
                        "type": "warn",
                        "source": "default",
                    }
                )

        # Check custom rules from DB
        rules = await self.get_rules()
        for rule in rules:
            if rule.pattern_type == "word":
                if rule.pattern.lower() in text_lower:
                    self._apply_rule(result, rule)
            elif rule.pattern_type == "regex":
                try:
                    if re.search(rule.pattern, text, re.IGNORECASE):
                        self._apply_rule(result, rule)
                except re.error:
                    pass

        # AI-based check for context
        if result["action"] in ["allow", "warn"]:
            ai_result = await ai_service.check_censorship(text)
            result["ai_check"] = ai_result

            if not ai_result.get("safe", True):
                result["action"] = "review"
                result["passed"] = False

        # Log the check
        if result["matched_rules"] or result["action"] != "allow":
            log = CensorshipLog(
                post_id=post_id,
                text=text[:1000],
                rule_id=None,
                matched_pattern=str(result["matched_rules"]),
                action=result["action"],
            )
            self.db.add(log)
            await self.db.commit()

        return result

    def _apply_rule(self, result: dict, rule: CensorshipRule):
        result["matched_rules"].append(
            {
                "pattern": rule.pattern,
                "type": rule.rule_type,
                "source": "database",
            }
        )

        if rule.rule_type == "banned":
            result["passed"] = False
            result["action"] = "reject"
        elif rule.rule_type == "warn":
            if result["action"] == "allow":
                result["action"] = "warn"
        elif rule.rule_type == "review":
            result["action"] = "review"
            result["passed"] = False

    async def auto_edit(self, text: str) -> str:
        rules = await self.get_rules()
        result_text = text

        for rule in rules:
            if rule.rule_type == "auto_edit" and rule.replacement:
                if rule.pattern_type == "word":
                    pattern = re.compile(re.escape(rule.pattern), re.IGNORECASE)
                    result_text = pattern.sub(rule.replacement, result_text)
                elif rule.pattern_type == "regex":
                    try:
                        result_text = re.sub(
                            rule.pattern, rule.replacement, result_text, flags=re.IGNORECASE
                        )
                    except re.error:
                        pass

        return result_text


async def check_censorship(db: AsyncSession, text: str, post_id: Optional[int] = None) -> dict:
    service = CensorshipService(db)
    return await service.check_text(text, post_id)
