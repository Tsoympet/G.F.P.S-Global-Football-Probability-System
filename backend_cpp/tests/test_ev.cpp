#include <catch2/catch_all.hpp>
#include "services/EVEngine.h"

TEST_CASE("EV calculation") {
    services::EVEngine ev;
    REQUIRE(ev.expectedValue(0.5, 2.0) == Approx(0.0));
    REQUIRE(ev.expectedValue(0.6, 2.5) == Approx(0.5));
}

TEST_CASE("Invalid odds") {
    services::EVEngine ev;
    REQUIRE(ev.expectedValue(0.5, -1.0) < 0);
}
