#include <iostream>

int main() {
    // summation of 1 to 10_000_000
    long long sum = 0;
    for (int i = 1; i <= 10'000'000; ++i) {
        sum += i;
    }
    std::cout << sum << std::endl;

    long long expected = 50000005000000;
    if (sum != expected) {
        std::cout << "Wrong answer: " << sum << std::endl;
        std::cout << "Expected: " << expected << std::endl;
    } else {
        std::cout << "Correct!" << std::endl;
    }

    return 0;
}
