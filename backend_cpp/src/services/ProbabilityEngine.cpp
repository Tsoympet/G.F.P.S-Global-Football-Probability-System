#include "ProbabilityEngine.h"

#include <cmath>
#include <algorithm>

namespace {
double poissonProb(int k, double lambda) {
    if (lambda <= 0) return 0.0;
    return std::pow(lambda, k) * std::exp(-lambda) / std::tgamma(k + 1);
}
}

namespace services {

Probabilities ProbabilityEngine::compute1X2(double homeGoals, double awayGoals) const {
    const int maxGoals = 10;
    double homeWin = 0.0, draw = 0.0, awayWin = 0.0;
    homeGoals = std::max(homeGoals, 0.01);
    awayGoals = std::max(awayGoals, 0.01);

    for (int i = 0; i <= maxGoals; ++i) {
        const double pHome = poissonProb(i, homeGoals);
        for (int j = 0; j <= maxGoals; ++j) {
            const double pAway = poissonProb(j, awayGoals);
            const double joint = pHome * pAway;
            if (i > j) homeWin += joint;
            else if (i == j) draw += joint;
            else awayWin += joint;
        }
    }

    const double total = homeWin + draw + awayWin;
    if (total > 0) {
        homeWin /= total;
        draw /= total;
        awayWin /= total;
    }

    return {homeWin, draw, awayWin};
}

}  // namespace services
