from src.agent.analyzer import CampaignIntelligenceAnalyzer
from src.agent.models import ObservationSeverity


def test_analyzer_detects_material_conversion_gap():
    analyzer = CampaignIntelligenceAnalyzer()

    observations = analyzer.analyze(
        "CMP-001",
        {
            "conversion_rate": 0.02,
            "conversion_benchmark": 0.04,
        },
    )

    assert len(observations) == 1
    assert observations[0].severity == ObservationSeverity.HIGH
    assert observations[0].category == "Conversion"
    assert observations[0].evidence["conversion_rate"] == 0.02


def test_analyzer_detects_moderate_conversion_gap():
    analyzer = CampaignIntelligenceAnalyzer()

    observations = analyzer.analyze(
        "CMP-002",
        {
            "Conversion Rate": 3.0,
            "Conversion Benchmark": 4.0,
        },
    )

    assert observations[0].severity == ObservationSeverity.MEDIUM


def test_analyzer_accepts_percentage_and_decimal_rates():
    analyzer = CampaignIntelligenceAnalyzer()

    decimal = analyzer.analyze(
        "CMP-003",
        {"open_rate": 0.20},
    )
    percentage = analyzer.analyze(
        "CMP-004",
        {"Open Rate": 20},
    )

    assert decimal[0].evidence["open_rate"] == 0.20
    assert percentage[0].evidence["open_rate"] == 0.20


def test_analyzer_detects_low_engagement():
    analyzer = CampaignIntelligenceAnalyzer()

    observations = analyzer.analyze(
        "CMP-005",
        {
            "open_rate": 0.20,
            "click_rate": 0.03,
        },
    )

    categories = {(item.category, item.title) for item in observations}

    assert ("Engagement", "Email engagement is low") in categories
    assert ("Engagement", "Click engagement is low") in categories


def test_analyzer_detects_low_qualified_audience_share():
    analyzer = CampaignIntelligenceAnalyzer()

    observations = analyzer.analyze(
        "CMP-006",
        {
            "marketable_contacts": 2000,
            "mql_count": 100,
        },
    )

    assert any(item.category == "Audience" for item in observations)
    assert any("Qualified audience" in item.title for item in observations)


def test_analyzer_detects_low_lead_intent():
    analyzer = CampaignIntelligenceAnalyzer()

    observations = analyzer.analyze(
        "CMP-007",
        {"average_lead_score": 42},
    )

    assert observations[0].category == "Lifecycle"
    assert observations[0].severity == ObservationSeverity.MEDIUM


def test_analyzer_detects_strong_lead_intent():
    analyzer = CampaignIntelligenceAnalyzer()

    observations = analyzer.analyze(
        "CMP-008",
        {"Average contact lead score": 84},
    )

    assert observations[0].severity == ObservationSeverity.LOW
    assert "strong lead intent" in observations[0].title


def test_analyzer_returns_positive_observation_when_performance_meets_benchmark():
    analyzer = CampaignIntelligenceAnalyzer()

    observations = analyzer.analyze(
        "CMP-009",
        {
            "conversion_rate": 0.05,
            "conversion_benchmark": 0.04,
        },
    )

    assert len(observations) == 1
    assert observations[0].severity == ObservationSeverity.INFO
    assert "at or above benchmark" in observations[0].title


def test_analyzer_does_not_invent_missing_metrics():
    analyzer = CampaignIntelligenceAnalyzer()

    observations = analyzer.analyze("CMP-010", {})

    assert len(observations) == 1
    assert observations[0].evidence == {}


def test_summary_identifies_highest_severity():
    analyzer = CampaignIntelligenceAnalyzer()

    observations = analyzer.analyze(
        "CMP-011",
        {
            "conversion_rate": 0.01,
            "conversion_benchmark": 0.04,
            "open_rate": 0.20,
        },
    )

    summary = analyzer.summarize(observations)

    assert summary["observation_count"] == 2
    assert summary["highest_severity"] == "High"
    assert summary["highest_priority_observation"] == "Conversion performance requires review"
