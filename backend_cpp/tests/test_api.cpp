#include <catch2/catch_all.hpp>
#include <nlohmann/json.hpp>
#include "services/ProbabilityEngine.h"

TEST_CASE("Probability output structure") {
    services::ProbabilityEngine engine;
    auto probs = engine.compute1X2(1.0, 1.0);
    REQUIRE(probs.homeWin >= 0.0);
    REQUIRE(probs.draw >= 0.0);
    REQUIRE(probs.awayWin >= 0.0);
}
