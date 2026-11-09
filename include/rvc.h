#ifndef RVC_H
#define RVC_H
#include <stdbool.h>
#include <stdio.h>
#ifdef __cplusplus
extern "C" {
#endif

typedef enum { FORWARD, BACKWARD, TURN_LEFT, TURN_RIGHT } Motion;
typedef enum { MOVING, REVERSING, TURNING } MovementState;
typedef enum { SENSOR_INVALID = -1, SENSOR_EOF = 0, SENSOR_VALID = 1 } SensorStatus;
typedef struct { bool front, left, right, dust; } Observation;
typedef struct { Observation observation; bool all_blocked; } Conditions;
typedef struct { bool enabled, mop; int power; } Cleaning;
typedef struct {
    unsigned tick;
    MovementState previous, current;
    unsigned state_ticks, boost_remaining;
    bool dust_pending, boost_active;
    Motion selected_turn;
} FsmSnapshot;
typedef struct { Motion motion; Cleaning cleaning; FsmSnapshot snapshot; } Decision;
typedef struct { Motion motion; Cleaning cleaning; } Intents;
typedef struct Fsm Fsm;

/* Opaque context lifetime helpers; only step_fsm accesses its private state. */
Fsm *fsm_create(void);
void fsm_destroy(Fsm *fsm);
Observation observe_obstacles(bool front, bool left, bool right);
bool observe_dust(bool dust);
SensorStatus acquire_sensors(FILE *input, Observation *observation);
Conditions build_conditions(Observation observation);
Decision step_fsm(Fsm *fsm, Conditions conditions);
Decision evaluate_behavior(Fsm *fsm, Observation observation);
Intents split_intents(Decision decision);
Intents compute_control(Fsm *fsm, Observation observation, FsmSnapshot *snapshot);
void send_motion(FILE *output, Motion motion);
void send_cleaning(FILE *output, Cleaning cleaning);
void deliver_commands(FILE *output, Intents intents);
int rvc_controller(FILE *input, FILE *output);

#ifdef __cplusplus
}
#endif
#endif
