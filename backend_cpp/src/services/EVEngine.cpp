#include "EVEngine.h"

#include <algorithm>

namespace services {

double EVEngine::expectedValue(double probability, double odds) const {
    probability = std::clamp(probability, 0.0, 1.0);
    if (odds <= 0.0) return -1.0;
    return probability * odds - 1.0;
}

}  // namespace services
