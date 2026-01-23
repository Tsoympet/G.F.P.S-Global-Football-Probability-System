#pragma once

#include <tuple>

namespace services {
struct Probabilities {
    double homeWin;
    double draw;
    double awayWin;
};

class ProbabilityEngine {
  public:
    Probabilities compute1X2(double homeGoals, double awayGoals) const;
};
}  // namespace services
