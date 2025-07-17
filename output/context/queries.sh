mbc_context="$1"

if [ "$mbc_context" = "ma-TA" ]; then
    query="-e 2 -f +causative+alienable-past-locative-number-pause -f +tense-past-determiner-locative-conditional -b"
elif [ "$mbc_context" = "na-TA" ]; then
    query="-e 2 -f +causative+alienable+past-locative-number-pause -f +tense+past-determiner-locative-conditional -b"
elif [ "$mbc_context" = "ma-det-TA" ]; then
    query="-e 3 -f +causative+alienable-past-locative-number-pause -f +determiner-goal-tense-causative -f +tense-past-determiner-locative-conditional -b"
elif [ "$mbc_context" = "na-det-TA" ]; then
    query="-e 3 -f +causative+alienable+past-locative-number-pause -f +determiner-goal-tense-causative -f +tense+past-determiner-locative-conditional -b"
fi
