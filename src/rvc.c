#include "rvc.h"
#include <string.h>

Observation observe_obstacles(bool front, bool left, bool right)
{
    Observation observation = {front, left, right, false};
    return observation;
}

bool observe_dust(bool dust)
{
    return dust;
}

SensorStatus acquire_sensors(FILE *input, Observation *observation)
{
    char line[128], extra;
    int front, left, right, dust;
    if (input == NULL || observation == NULL) return SENSOR_INVALID;
    if (fgets(line, sizeof line, input) == NULL) return feof(input) ? SENSOR_EOF : SENSOR_INVALID;
    if (strchr(line, '\n') == NULL && !feof(input)) return SENSOR_INVALID;
    if (sscanf(line, "%d %d %d %d %c", &front, &left, &right, &dust, &extra) != 4)
        return SENSOR_INVALID;
    if ((front != 0 && front != 1) || (left != 0 && left != 1) ||
        (right != 0 && right != 1) || (dust != 0 && dust != 1)) return SENSOR_INVALID;
    *observation = observe_obstacles(front != 0, left != 0, right != 0);
    observation->dust = observe_dust(dust != 0);
    return SENSOR_VALID;
}

Conditions build_conditions(Observation observation)
{
    Conditions conditions = {observation, observation.front && observation.left && observation.right};
    return conditions;
}

Decision evaluate_behavior(Fsm *fsm, Observation observation)
{
    return step_fsm(fsm, build_conditions(observation));
}

Intents split_intents(Decision decision)
{
    Intents intents = {decision.motion, decision.cleaning};
    return intents;
}

Intents compute_control(Fsm *fsm, Observation observation, FsmSnapshot *snapshot)
{
    Decision decision = evaluate_behavior(fsm, observation);
    if (snapshot != NULL) *snapshot = decision.snapshot;
    return split_intents(decision);
}

void send_motion(FILE *output, Motion motion)
{
    static const char *const names[] = {"FORWARD", "BACKWARD", "TURN_LEFT", "TURN_RIGHT"};
    if (output == NULL) return;
    if (motion < FORWARD || motion > TURN_RIGHT) return;
    fprintf(output, "\"motor\":\"%s\",", names[motion]);
}

void send_cleaning(FILE *output, Cleaning cleaning)
{
    if (output == NULL) return;
    fprintf(output, "\"cleaner\":{\"enabled\":%s,\"mop\":%s,\"power\":%d}",
            cleaning.enabled ? "true" : "false", cleaning.mop ? "true" : "false", cleaning.power);
}

void deliver_commands(FILE *output, Intents intents)
{
    send_motion(output, intents.motion);
    send_cleaning(output, intents.cleaning);
}

int rvc_controller(FILE *input, FILE *output)
{
    static const char *const states[] = {"FORWARD", "BACKWARD", "TURNING"};
    Observation observation;
    FsmSnapshot snapshot;
    Fsm *fsm;
    SensorStatus status;
    if (input == NULL || output == NULL) return 2;
    fsm = fsm_create();
    if (fsm == NULL) return 3;
    while ((status = acquire_sensors(input, &observation)) == SENSOR_VALID) {
        Intents intents = compute_control(fsm, observation, &snapshot);
        fprintf(output, "{\"tick\":%u,\"sensors\":{\"front\":%d,\"left\":%d,\"right\":%d,\"dust\":%d},",
                snapshot.tick, observation.front, observation.left, observation.right, observation.dust);
        deliver_commands(output, intents);
        fprintf(output, ",\"previous_state\":\"%s\",\"state\":\"%s\",\"state_ticks\":%u,"
                "\"boost_remaining\":%u,\"boost_active\":%s,\"dust_pending\":%s,\"selected_turn\":%d,"
                "\"all_blocked\":%s}\n",
                states[snapshot.previous], states[snapshot.current], snapshot.state_ticks,
                snapshot.boost_remaining, snapshot.boost_active ? "true" : "false",
                snapshot.dust_pending ? "true" : "false", snapshot.selected_turn,
                observation.front && observation.left && observation.right ? "true" : "false");
        fflush(output);
    }
    fsm_destroy(fsm);
    return status == SENSOR_EOF ? 0 : 2;
}
