from artifactproof.requirement_parser import RequirementSpec, parse_requirement_file


def test_parse_requirement_yaml():
    spec = parse_requirement_file("benchmark/discount_engine/requirement.yaml")
    assert isinstance(spec, RequirementSpec)
    assert spec.id == "discount_engine_01"
    assert spec.artifact.file == "discount_engine.py"
    assert spec.artifact.class_name == "DiscountEngine"
    assert "calculate_discount" in spec.artifact.functions
    assert spec.consumer.file == "checkout.py"
    assert spec.consumer.class_name == "CheckoutService"
    assert spec.tests.relevant[0].endswith("test_discount.py")
