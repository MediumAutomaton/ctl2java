package org.firstinspires.ftc.teamcode.framework.ctlpad.CTL2Java.test;


import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
import org.firstinspires.ftc.teamcode.framework.ctlpad.CTL2Java.CTLtest;

@TeleOp()
public class TestSchemeStatePrinter extends OpMode {

    TestSchemeInterface scheme;

    @Override
    public void init() {
        scheme = new CTLtest(gamepad1, gamepad2);
    }

    @Override
    public void loop() {
        TestSchemeState state = scheme.getState();

        telemetry.addData("ActionOne", state.isActionOne());
        telemetry.addData("ActionTwo", state.getActionTwo());
        telemetry.addData("ModifierActionOne", state.isModifierActionOne());
        telemetry.addData("ModifierActionTwo", state.isModifierActionTwo());

        telemetry.update();
    }
}
