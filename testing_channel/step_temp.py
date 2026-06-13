
import asyncio
# print("imported the whole reranking")
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from retrieval.Unified_retrieval_manager import UnifiedRetrievalResult
from retrieval.retrieval_manager import retrivel_search
from postprocessing.fusion import fuse_result
from postprocessing.deduplication import deduplicate
from postprocessing.reranking_v2 import reranker
from generation.context_builder import build_context
from generation.prompt_builder import build_prompt
from generation.answer import generate_answer
from generation.cititation_map import build_citation_map, append_references
query = """
Why did modern CPU architectures move from increasing clock speeds to increasing core counts, and what engineering trade-offs shaped this transition?
"""


async def run_pipeline(
#     request_id: str,
    query: str
):
    try:
        # from translate_chunk.extended_queries import get_extended_query
        # extend_query = await get_extended_query(query)
        print("inside the pipeline")
        # from retrieval.retrieval_manager import retrivel_search
        retrieval_bundle = await retrivel_search(query)
        print("retreivel completed")

        results = retrieval_bundle["results"]
        # from postprocessing.fusion import fuse_result
        fused = fuse_result(results)
        # from postprocessing.deduplication import deduplicate
        deduped = deduplicate(fused)
        # from postprocessing.reranking_v2 import reranker
        reranked = await reranker(deduped)

        top_k = reranked[:8]
        # from generation.context_builder import build_context
        context = build_context(top_k)
        
        # from generation.prompt_builder import  build_prompt
        prompt = build_prompt(
            query,
            context,
            intent="general"
        )
        # from generation.answer import generate_answer

        answer = await generate_answer(prompt)
        from generation.cititation_map import build_citation_map , append_references
        citation_map = build_citation_map(top_k)

        final_answer = append_references(
            answer,
            citation_map
        )
        return final_answer
    except Exception as e:
        print(f"e")
            
if __name__ == "__main__":

    from pprint import pprint
    pprint(asyncio.run(run_pipeline("explain the type of Machine learning(LLM's) security vulnerability or the challenges in Machine learning Security")))
