#include "rvc.h"
#include <stdlib.h>
struct Fsm { FsmSnapshot value; };
static Motion choose_turn(Observation input)
{
    return input.left && !input.right ? TURN_RIGHT : TURN_LEFT;
}
Fsm *fsm_create(void)
{
    Fsm *fsm = calloc(1, sizeof(Fsm));
    if (fsm != NULL) fsm->value.selected_turn = TURN_LEFT;
    return fsm;
}
void fsm_destroy(Fsm *fsm) { free(fsm); }
Decision step_fsm(Fsm *fsm, Conditions conditions)
{
    Decision decision = {0};
    FsmSnapshot *state;
    Observation input = conditions.observation;
    if (fsm == NULL) return decision;
    state = &fsm->value;
    state->previous = state->current;
    state->tick++;

    if (state->current == REVERSING) {
        state->current = TURNING;
        state->selected_turn = choose_turn(input);
    } else {
        /* A turn completes in one model tick; recheck before moving forward. */
        state->current = MOVING;
        if (input.front) {
            if (conditions.all_blocked) {
                state->current = REVERSING;
            } else {
                state->current = TURNING;
                state->selected_turn = choose_turn(input);
            }
        }
    }
    state->state_ticks = state->current == state->previous ? state->state_ticks + 1 : 1;
    decision.motion = state->current == REVERSING ? BACKWARD :
        state->current == TURNING ? state->selected_turn : FORWARD;
    decision.cleaning.enabled = state->current == MOVING;
    decision.cleaning.mop = decision.cleaning.enabled;
    state->boost_active = false;
    if (decision.cleaning.enabled) {
        if (input.dust || state->dust_pending) state->boost_remaining = 3;
        state->dust_pending = false;
        state->boost_active = state->boost_remaining > 0;
        decision.cleaning.power = state->boost_active ? 2 : 1;
        if (state->boost_remaining > 0) state->boost_remaining--;
    } else {
        state->dust_pending = state->dust_pending || input.dust;
        decision.cleaning.power = 0;
    }
    decision.snapshot = *state;
    return decision;
}
