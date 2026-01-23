#include "ConfidenceEngine.h"

#include <algorithm>

namespace services {

double ConfidenceEngine::score(const Probabilities& probs) const {
    double maxProb = std::max({probs.homeWin, probs.draw, probs.awayWin});
    return maxProb;
}

}  // namespace services
