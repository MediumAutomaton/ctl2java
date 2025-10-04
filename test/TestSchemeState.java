package org.firstinspires.ftc.teamcode.framework.ctlpad.CTL2Java.test;

public class TestSchemeState {

    private boolean actionOne = false;
    private double actionTwo = 0.0;
    private boolean modifierActionOne = false;
    private boolean modifierActionTwo = false;

    public boolean isActionOne() {
        return actionOne;
    }

    public void setActionOne(boolean actionOne) {
        this.actionOne = actionOne;
    }

    public double getActionTwo() {
        return actionTwo;
    }

    public void setActionTwo(double actionTwo) {
        this.actionTwo = actionTwo;
    }

    public boolean isModifierActionOne() {
        return modifierActionOne;
    }

    public void setModifierActionOne(boolean modifierActionOne) {
        this.modifierActionOne = modifierActionOne;
    }

    public boolean isModifierActionTwo() {
        return modifierActionTwo;
    }

    public void setModifierActionTwo(boolean modifierActionTwo) {
        this.modifierActionTwo = modifierActionTwo;
    }

}
