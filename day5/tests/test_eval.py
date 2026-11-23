# pip install deepeval
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

def test_answer_relevancy():
    test_case = LLMTestCase(
        input="What is the VAT rate in France?",
        actual_output="The standard VAT rate in France is 20%.",
    )
    metric = AnswerRelevancyMetric(threshold=0.7)
    metric.measure(test_case)
    assert metric.is_successful()
