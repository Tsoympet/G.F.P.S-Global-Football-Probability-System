#pragma once

#include "ProbabilityEngine.h"

namespace services {
class ConfidenceEngine {
  public:
    double score(const Probabilities& probs) const;
};
}  // namespace services
