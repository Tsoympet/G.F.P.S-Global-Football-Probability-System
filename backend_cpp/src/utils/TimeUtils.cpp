#include "TimeUtils.h"

namespace utils {

int64_t TimeUtils::toUnix(const trantor::Date& date) {
    return date.microSecondsSinceEpoch() / 1'000'000;
}

}  // namespace utils
