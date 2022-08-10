OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
h q[0];
h q[1];
x q[3];
ccx q[0], q[1], q[2];

