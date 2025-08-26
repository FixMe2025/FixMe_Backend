import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    pipeline,
)
import traceback
from .config import settings
from app import diff_match_patch as dmp_module
from langgraph.graph import StateGraph, END
from .state_models import GraphState
from .workflow.nodes import WorkflowNodes


class AdvancedSpellCheckService:
    def __init__(self):
        self.device = None
        self.tokenizer_base = None
        self.model_base = None
        self.pipe_lm = None
        self.dmp = dmp_module.diff_match_patch()
        self._initialize_models()
        self.workflow = self._build_graph()

    def _initialize_models(self):
        """두 개의 언어 모델을 초기화하고 로드합니다."""
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Using device: {self.device}")

            # 1. 기본 교정 모델 (kogrammar-base)
            print("Loading kogrammar-base model...")
            self.tokenizer_base = AutoTokenizer.from_pretrained(settings.MODEL_NAME)
            self.model_base = AutoModelForSeq2SeqLM.from_pretrained(settings.MODEL_NAME)
            self.model_base.to(self.device)
            print("kogrammar-base model loaded.")

            # 2. LLM 기반 교정 모델 (j5ng/et5-typos-corrector)
            print("Loading j5ng/et5-typos-corrector model...")
            lm_model_name = "j5ng/et5-typos-corrector"

            model = AutoModelForSeq2SeqLM.from_pretrained(
                lm_model_name,
                torch_dtype=torch.bfloat16,
                device_map="auto",
            )
            tokenizer = AutoTokenizer.from_pretrained(lm_model_name)

            self.pipe_lm = pipeline(
                "text2text-generation",
                model=model,
                tokenizer=tokenizer,
            )
            print("j5ng/et5-typos-corrector model loaded.")

        except Exception as e:
            print(f"Error during model initialization: {e}")
            traceback.print_exc()
            self.model_base = None
            self.pipe_lm = None

    def is_model_loaded(self) -> bool:
        return self.model_base is not None and self.pipe_lm is not None

    def get_device_info(self) -> str:
        return str(self.device)




    def _build_graph(self):
        """LangGraph 워크플로우를 정의하고 컴파일합니다."""
        nodes = WorkflowNodes(
            self.tokenizer_base,
            self.model_base,
            self.pipe_lm,
            self.device,
            self.dmp
        )
        
        workflow = StateGraph(GraphState)
        workflow.add_node("smart_text_splitting", nodes.smart_text_splitting)
        workflow.add_node("initial_correction", nodes.initial_correction)
        workflow.add_node("refine_correction", nodes.refine_correction)
        workflow.add_node("generate_suggestions", nodes.generate_suggestions)
        workflow.add_node("generate_diff", nodes.generate_diff)

        workflow.set_entry_point("smart_text_splitting")
        workflow.add_edge("smart_text_splitting", "initial_correction")
        workflow.add_edge("initial_correction", "refine_correction")
        workflow.add_edge("refine_correction", "generate_suggestions")
        workflow.add_edge("generate_suggestions", "generate_diff")
        workflow.add_edge("generate_diff", END)

        return workflow.compile()

    def correct_text(self, text: str) -> dict:
        """LangGraph를 사용하여 다단계 맞춤법 교정을 실행합니다."""
        if not self.is_model_loaded():
            return {
                "error": "교정 모델이 로드되지 않았습니다. 서버 로그를 확인해주세요."
            }

        inputs = {
            "original_text": text,
            "corrected_text": "",
            "corrections": [],
            "error": "",
            "text_chunks": [],
            "processed_chunks": [],
            "suggestions": [],
        }
        result_state = self.workflow.invoke(inputs)

        if result_state.get("error"):
            raise Exception(result_state["error"])

        return {
            "original_text": result_state["original_text"],
            "corrected_text": result_state["corrected_text"],
            "corrections": result_state["corrections"],
            "suggestions": result_state.get("suggestions", []),
        }


# 싱글톤 인스턴스
advanced_spellcheck_service = AdvancedSpellCheckService()
