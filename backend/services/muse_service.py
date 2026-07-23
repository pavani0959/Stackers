import json
import logging
from typing import Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
from google import genai

from config import get_settings
from ml import muse_chat_response
from repositories.recommendation_repository import RecommendationRepository
from services.decision_score_calculator import DecisionScoreCalculator
from schemas import MuseResponse, ProductResponse
import models

logger = logging.getLogger(__name__)

def _product_to_dict(product: models.Product) -> dict[str, Any]:
    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "brand": product.brand,
        "description": product.description,
        "price": product.price,
        "originalPrice": product.originalPrice,
        "image": product.image,
        "category": product.category,
        "subcategory": product.subcategory,
        "primary_colour": product.primary_colour,
        "gender_segment": product.gender_segment,
        "tags": list(product.tags or []),
        "occasions": list(product.occasions or []),
        "sizes": list(product.sizes or []),
        "budgetTier": product.budgetTier,
        "season": product.season,
        "stock_quantity": product.stock_quantity,
        "is_active": product.is_active,
    }

class GeminiMuseResponse(BaseModel):
    reply: str
    recommended_product_ids: list[int]
    intent: str

class MuseService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.repo = RecommendationRepository(db)
        if self.settings.gemini_api_key:
            self.client = genai.Client(api_key=self.settings.gemini_api_key)
        else:
            self.client = None

    def chat(self, message: str, user_id: int) -> dict[str, Any]:
        # Fallback if no client
        if not self.client:
            logger.info("MuseService: No Gemini API key, falling back to rule-based.")
            return self._fallback_chat(message, user_id)

        try:
            # 1. Fetch user data
            user = self.repo.get_user(user_id)
            if not user:
                return self._fallback_chat(message, user_id)
                
            style_profile = self.repo.get_latest_style_profile(user_id)
            preferences = self.repo.get_preferences(user_id)
            wardrobe_items = self.repo.get_active_wardrobe_items(user_id)
            memory_entries = self.repo.list_memory_entries(user_id=user_id)[:5]

            # Extract info for context
            dna = style_profile.dna_vector if style_profile else {}
            budget_tier = preferences.budget_tier if preferences else "standard"
            wardrobe = [
                {
                    "product_id": w.product_id,
                    "category": w.category,
                    "name": getattr(w, "name", "Item")
                } 
                for w in wardrobe_items
            ]
            recent_memory = [
                {
                    "event": entry[0].event_type, 
                    "product_name": entry[1].product_snapshot.get("name"),
                    "category": entry[1].product_snapshot.get("category")
                } 
                for entry in memory_entries
            ]

            # 2. Get top 15 candidate products
            all_products = self.repo.list_active_products()
            
            calculator = DecisionScoreCalculator()
            
            scored = []
            for p in all_products:
                res = calculator.calculate(
                    style_profile=style_profile,
                    preferences=preferences,
                    product=p,
                    wardrobe_items=wardrobe_items,
                    context={}
                )
                scored.append((res["overall_score"], p))
                
            scored.sort(key=lambda x: x[0], reverse=True)
            top_products = scored[:15]

            products_context = [
                {
                    "id": p.id,
                    "name": p.name,
                    "brand": p.brand,
                    "price": float(p.price),
                    "category": p.category,
                    "tags": p.tags
                }
                for _, p in top_products
            ]

            # 3. Build system prompt
            system_prompt = f"""You are Myntra Muse, an AI personal stylist for the user '{user.name}'.
Your role is to answer their fashion queries, recommend products, and assist with styling.
IMPORTANT RULES:
1. ONLY recommend products from the CANDIDATE PRODUCTS list below. Provide their exact integer IDs in 'recommended_product_ids'.
2. DO NOT hallucinate purchase behavior, savings, or return stats. If the user asks about something not in the DATA CONTEXT, say "I don't have data on that."
3. Your response MUST be valid JSON conforming exactly to this schema:
{{
  "reply": "Your message to the user",
  "recommended_product_ids": [1, 5],
  "intent": "recommendation"
}}
4. Keep the reply short and conversational.

DATA CONTEXT:
User DNA Vector: {json.dumps(dna)}
User Budget Tier: {budget_tier}
Wardrobe Items: {json.dumps(wardrobe)}
Last 5 Memory Events: {json.dumps(recent_memory)}

CANDIDATE PRODUCTS:
{json.dumps(products_context, indent=2)}
"""

            # 4. Call Gemini
            logger.info("MuseService: Calling Gemini API...")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=message,
                config={
                    "system_instruction": system_prompt,
                    "response_mime_type": "application/json",
                    "response_schema": GeminiMuseResponse.model_json_schema()
                }
            )

            # 5. Parse and build final response
            result = GeminiMuseResponse.model_validate_json(response.text)
            
            # Map ids to products
            recommended_products = []
            for pid in result.recommended_product_ids:
                for _, p in top_products:
                    if p.id == pid:
                        recommended_products.append(_product_to_dict(p))
                        break

            logger.info("MuseService: Gemini call succeeded.")
            return {
                "reply": result.reply,
                "intent": result.intent,
                "recommendations": recommended_products
            }
            
        except Exception as e:
            logger.warning(f"MuseService: Gemini API failed or parsing failed: {e}. Falling back.")
            return self._fallback_chat(message, user_id)

    def _fallback_chat(self, message: str, user_id: int) -> dict[str, Any]:
        # Emulate the old main.py behavior exactly
        from ml import muse_chat_response
        user = self.repo.get_user(user_id)
        style_profile = self.repo.get_latest_style_profile(user_id)
        preferences = self.repo.get_preferences(user_id)
        memory_entries = self.repo.list_memory_entries(user_id=user_id)
        
        # Build user_profile dict matching what old muse_chat_response expected
        user_profile = {
            "name": user.name if user else "User",
            "identityName": style_profile.primary_identity if style_profile else "Fashion Profile",
            "dna": style_profile.dna_vector if style_profile else {},
            "budget": preferences.budget_tier if preferences else "standard",
            "purchaseMemory": [
                {
                    "name": entry[1].product_snapshot.get("name"),
                    "dnaMatch": entry[1].overall_score
                }
                for entry in memory_entries
            ]
        }
        
        all_products = self.repo.list_active_products()
        products_dict = [_product_to_dict(p) for p in all_products]
        
        return muse_chat_response(message, user_profile, products_dict)
