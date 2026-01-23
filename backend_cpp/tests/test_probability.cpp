#include <catch2/catch_all.hpp>
#include "services/ProbabilityEngine.h"

TEST_CASE("Probability sums to 1") {
    services::ProbabilityEngine engine;
    auto probs = engine.compute1X2(1.5, 1.2);
    REQUIRE(probs.homeWin + probs.draw + probs.awayWin == Approx(1.0).margin(0.001));
}

TEST_CASE("Higher goals increases win prob") {
    services::ProbabilityEngine engine;
    auto favored = engine.compute1X2(2.5, 0.8);
    auto underdog = engine.compute1X2(0.8, 2.5);
    REQUIRE(favored.homeWin > underdog.homeWin);
}
