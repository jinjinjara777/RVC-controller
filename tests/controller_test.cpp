#include <gtest/gtest.h>
#include "rvc.h"
#include <string>

class ControllerTest : public ::testing::Test {
protected:
    Fsm *fsm = nullptr;
    void SetUp() override { fsm = fsm_create(); ASSERT_NE(fsm, nullptr); }
    void TearDown() override { fsm_destroy(fsm); }
    Decision tick(bool f=false, bool l=false, bool r=false, bool d=false) {
        return evaluate_behavior(fsm, Observation{f,l,r,d});
    }
};

TEST_F(ControllerTest, R1_R2_ForwardCleansAndMops) {
    auto d=tick(); EXPECT_EQ(d.motion,FORWARD); EXPECT_TRUE(d.cleaning.enabled);
    EXPECT_TRUE(d.cleaning.mop); EXPECT_EQ(d.cleaning.power,1); EXPECT_EQ(d.snapshot.tick,1u);
}
TEST_F(ControllerTest, R3_LeftPreferredAndCleaningStops) {
    auto d=tick(true); EXPECT_EQ(d.motion,TURN_LEFT); EXPECT_FALSE(d.cleaning.enabled);
    EXPECT_FALSE(d.cleaning.mop); EXPECT_EQ(d.cleaning.power,0);
}
TEST_F(ControllerTest, R3_RightWhenLeftBlocked) { EXPECT_EQ(tick(true,true).motion,TURN_RIGHT); }
TEST_F(ControllerTest, R3_LeftWhenRightBlocked) { EXPECT_EQ(tick(true,false,true).motion,TURN_LEFT); }
TEST_F(ControllerTest, R3_ResumesAfterTurn) {
    tick(true); auto d=tick(); EXPECT_EQ(d.motion,FORWARD); EXPECT_TRUE(d.cleaning.enabled);
    EXPECT_EQ(d.snapshot.previous,TURNING); EXPECT_EQ(d.snapshot.current,MOVING);
}
TEST_F(ControllerTest, R4_BackThenTurnThenResume) {
    auto back=tick(true,true,true); EXPECT_EQ(back.motion,BACKWARD); EXPECT_FALSE(back.cleaning.enabled);
    auto turn=tick(); EXPECT_EQ(turn.motion,TURN_LEFT); EXPECT_EQ(turn.snapshot.previous,REVERSING);
    auto forward=tick(); EXPECT_EQ(forward.motion,FORWARD); EXPECT_TRUE(forward.cleaning.enabled);
}
TEST_F(ControllerTest, R3_RechecksFrontAfterTurn) {
    tick(true); auto d=tick(true,true,false); EXPECT_EQ(d.motion,TURN_RIGHT); EXPECT_FALSE(d.cleaning.enabled);
}
TEST_F(ControllerTest, Profile_SideOnlyDoesNotInterruptForward) {
    EXPECT_EQ(tick(false,true,true).motion,FORWARD); EXPECT_TRUE(tick(false,true).cleaning.enabled);
}
TEST_F(ControllerTest, R5_ThreeActiveTicksThenNormal) {
    auto first=tick(false,false,false,true); EXPECT_EQ(first.cleaning.power,2);
    EXPECT_EQ(first.snapshot.boost_remaining,2u); EXPECT_TRUE(first.snapshot.boost_active);
    EXPECT_EQ(tick().cleaning.power,2); EXPECT_EQ(tick().cleaning.power,2);
    EXPECT_EQ(tick().cleaning.power,1);
}
TEST_F(ControllerTest, R5_RepeatedDustRefreshesDuration) {
    tick(false,false,false,true); tick();
    EXPECT_EQ(tick(false,false,false,true).snapshot.boost_remaining,2u);
    EXPECT_EQ(tick().cleaning.power,2); EXPECT_EQ(tick().cleaning.power,2); EXPECT_EQ(tick().cleaning.power,1);
}
TEST_F(ControllerTest, R3_R5_AvoidanceOverridesAndPausesBoost) {
    tick(false,false,false,true); auto avoid=tick(true);
    EXPECT_EQ(avoid.cleaning.power,0); EXPECT_EQ(avoid.snapshot.boost_remaining,2u);
    EXPECT_EQ(tick().cleaning.power,2);
}
TEST_F(ControllerTest, R3_R5_DustDuringAvoidanceIsPending) {
    auto d=tick(true,false,false,true); EXPECT_TRUE(d.snapshot.dust_pending); EXPECT_EQ(d.cleaning.power,0);
    d=tick(); EXPECT_FALSE(d.snapshot.dust_pending); EXPECT_EQ(d.cleaning.power,2);
}
TEST_F(ControllerTest, R4_R5_PendingSurvivesBackwardAndTurn) {
    tick(true,true,true,true); auto d=tick(); EXPECT_TRUE(d.snapshot.dust_pending);
    d=tick(); EXPECT_EQ(d.cleaning.power,2); EXPECT_EQ(d.snapshot.boost_remaining,2u);
}
TEST_F(ControllerTest, Profile_BackwardUsesCurrentOpenRight) {
    tick(true,true,true); EXPECT_EQ(tick(false,true,false).motion,TURN_RIGHT);
}
TEST_F(ControllerTest, R4_RepeatedEnclosureRemainsStopped) {
    tick(true,true,true); tick(true,true,true);
    EXPECT_EQ(tick(true,true,true).motion,BACKWARD);
}
TEST_F(ControllerTest, Profile_StateTickCountsAndIndependentContexts) {
    EXPECT_EQ(tick().snapshot.state_ticks,1u); EXPECT_EQ(tick().snapshot.state_ticks,2u);
    auto other=fsm_create(); auto d=evaluate_behavior(other,Observation{});
    EXPECT_EQ(d.snapshot.tick,1u); EXPECT_EQ(d.snapshot.current,MOVING); fsm_destroy(other);
}
TEST(Conditions,R3_R4_AllSensorCombinationsPreserveValues) {
    for(int mask=0;mask<16;mask++) {
        Observation o{bool(mask&1),bool(mask&2),bool(mask&4),bool(mask&8)};
        auto c=build_conditions(o); EXPECT_EQ(c.all_blocked,(mask&7)==7);
        EXPECT_EQ(c.observation.front,o.front); EXPECT_EQ(c.observation.left,o.left);
        EXPECT_EQ(c.observation.right,o.right); EXPECT_EQ(c.observation.dust,o.dust);
    }
}
static std::string run(const char *text,int *status=nullptr) {
    FILE *in=tmpfile(),*out=tmpfile(); if(!in || !out) return "IO failure";
    fputs(text,in); rewind(in); int code=rvc_controller(in,out); if(status) *status=code;
    rewind(out); std::string s; char buf[4096]; while(fgets(buf,sizeof buf,out)) s+=buf;
    fclose(in); fclose(out); return s;
}
TEST(Pipeline,R1_R5_ActualOutputAndReset) {
    auto s=run("0 0 0 1\n1 0 0 0\n0 0 0 0\n");
    EXPECT_NE(s.find("\"power\":2"),std::string::npos);
    EXPECT_NE(s.find("\"motor\":\"TURN_LEFT\""),std::string::npos);
    EXPECT_NE(s.find("\"tick\":3"),std::string::npos);
    EXPECT_NE(run("0 0 0 0\n").find("\"tick\":1"),std::string::npos);
}
TEST(Pipeline,InvalidInputIsRejectedWithoutCommand) {
    for(auto s:{"2 0 0 0\n","0 2 0 0\n","0 0 2 0\n","0 0 0 -1\n","0 0\n","0 0 0 0 junk\n"}) {
        int status=0; EXPECT_EQ(run(s,&status),""); EXPECT_EQ(status,2);
    }
    int status=-1; EXPECT_EQ(run("",&status),""); EXPECT_EQ(status,0);
}
TEST(Pipeline,NullPortsAndNullSnapshot) {
    EXPECT_EQ(rvc_controller(nullptr,stdout),2); EXPECT_EQ(rvc_controller(stdin,nullptr),2);
    Observation o{}; EXPECT_EQ(acquire_sensors(nullptr,&o),SENSOR_INVALID);
    FILE *in=tmpfile(); ASSERT_NE(in,nullptr); EXPECT_EQ(acquire_sensors(in,nullptr),SENSOR_INVALID); fclose(in);
    auto f=fsm_create(); EXPECT_TRUE(compute_control(f,Observation{},nullptr).cleaning.enabled); fsm_destroy(f);
    send_motion(nullptr,FORWARD); send_cleaning(nullptr,Cleaning{});
    FILE *out=tmpfile(); ASSERT_NE(out,nullptr); send_motion(out,static_cast<Motion>(99)); EXPECT_EQ(ftell(out),0); fclose(out);
    EXPECT_FALSE(step_fsm(nullptr,Conditions{}).cleaning.enabled);
}
TEST(Pipeline,FinalLineValidationDistinguishesMalformedInputFromEof) {
    int status=-1;
    EXPECT_EQ(run("2 0 0 0",&status),""); EXPECT_EQ(status,2);
    EXPECT_NE(run("0 0 0 0",&status).find("\"power\":1"),std::string::npos); EXPECT_EQ(status,0);
}
TEST(Pipeline,LongRecordIsRejectedAndAllBooleanEncodingsArePreserved) {
    int status=-1; std::string longLine(200,'0');longLine+='\n';
    EXPECT_EQ(run(longLine.c_str(),&status),""); EXPECT_EQ(status,2);
    EXPECT_NE(run("1 1 1 1\n0 1 0 0\n0 0 1 0\n").find("\"state\":\"BACKWARD\""),std::string::npos);
    EXPECT_NE(run("1 1 0 0\n").find("\"motor\":\"TURN_RIGHT\""),std::string::npos);
    for(auto input:{"-1 0 0 0\n","0 -1 0 0\n","0 0 -1 0\n","0 0 0 2\n"}){
        EXPECT_EQ(run(input,&status),""); EXPECT_EQ(status,2);
    }
}
