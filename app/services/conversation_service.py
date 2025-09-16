# app/services/conversation_service.py
from typing import Dict, Any
from app.models.conversation_models import ConversationRequest, ConversationResponse
from app.storage.conversation_store import ConversationStore

class ConversationService:
    """
    Async conversation orchestration. Uses async ConversationStore methods.
    """

    @staticmethod
    async def handle_turn(request: ConversationRequest) -> ConversationResponse:
        # Fetch current context (memory) for this call/session
        context = await ConversationStore.async_get_context(request.session_id)

        # AI analysis (Phase 3/4 reuse) — call the ai service
        # We expect there to be an async ai service function `respond_to_text`
        # It should return reply text and optionally parsed intent/entities
        from app.services.ai_service import respond_to_text, analyze_text  # local import to avoid circulars

        # analyze_text might be async or sync depending on your ai_service impl.
        # If analyze_text is async, await it; otherwise call directly.
        ai_analysis = {}
        try:
            # try async analyze_text
            ana = analyze_text  # may raise NameError if not present
            if callable(ana):
                # attempt await if coroutine function
                import inspect
                if inspect.iscoroutinefunction(ana):
                    ai_analysis = await ana(request.text)
                else:
                    ai_analysis = ana(request.text)
            else:
                ai_analysis = {}
        except Exception:
            ai_analysis = {}

        # fallback: generate textual reply (respond_to_text) — prefer async
        reply_text = ""
        try:
            if hasattr(respond_to_text, "__call__"):
                import inspect
                if inspect.iscoroutinefunction(respond_to_text):
                    reply_text = await respond_to_text(request.text, language=getattr(request, "language", "en"))
                else:
                    reply_text = respond_to_text(request.text, language=getattr(request, "language", "en"))
        except Exception as e:
            reply_text = f"[error-generating-reply] {type(e).__name__}"

        # Decide intent (defensive)
        intent = None
        entities = {}
        if isinstance(ai_analysis, dict):
            intent = ai_analysis.get("intent") or (ai_analysis.get("top_intent") if ai_analysis else None)
            entities = ai_analysis.get("entities") or {}

        # High-level routing (you can extend this)
        response_text = ConversationService._route_intent(intent, ai_analysis or {}, request, reply_text)

        # Save transcript into conversation store (async)
        await ConversationStore.async_save_turn(request.session_id, request.text, response_text)

        # Return ConversationResponse model instance
        return ConversationResponse(
            session_id=request.session_id,
            user_text=request.text,
            ai_text=response_text,
            intent=intent or "unknown",
            context=await ConversationStore.async_get_context(request.session_id),
        )

    @staticmethod
    def _route_intent(intent: str, ai_result: dict, request: ConversationRequest, generated_reply: str) -> str:
        """
        Lightweight routing on detected intent; if none, return generated_reply.
        """
        if intent == "inquiry":
            # Example: ask for clarifying details
            loc = ai_result.get("entities", {}).get("location") if isinstance(ai_result, dict) else None
            return f"I see you're interested in property at {loc or 'the specified location'}. Can I help with a site visit?"
        if intent == "greeting":
            return "Hello! How can I help with real-estate today?"
        if intent == "goodbye":
            return "Thanks — have a great day!"
        # default: use LLM reply
        return generated_reply or "I didn't quite get that — can you rephrase?"
