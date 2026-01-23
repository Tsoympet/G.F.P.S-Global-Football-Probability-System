#pragma once

#include <string>

namespace models {
struct Match {
    int id{};
    int homeTeamId{};
    int awayTeamId{};
    std::string kickoff;
    double homeExpectedGoals{};
    double awayExpectedGoals{};
};
}
