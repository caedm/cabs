import subprocess

with open('lala', 'w') as f:
    f.write("gatewayhostname:s:rdpgateway.et.byu.edu\n") #specifies the RD Gateway host name
    f.write("gatewayusagemethod:i:1\n") #Specifies when to use an RD Gateway for the connection 1="Always use RDP Gateway"
    f.write("promptcredentialonce:i:1\n") #Determines whether a user's credentials are saved and used for both RDP Gateway 1="same credentials used"
    f.write("gatewayprofileusagemethod:i:1\n") #Specifies whether to use default RD Gate. 1="explicit settings set by user"
    f.write("prompt for credentials:i:0\n") #determines whether a user's credentials are saved and used for both the RD Gateway and the remote computer. 0="Remote session will not use the same credentials" Should be 1?
    f.write('username:s:et.byu.edu\\%s\n' % 'haydent')
    f.write("full address:s:%s\n" % 'CBMOONSHOT1C16') 
    subprocess.Popen("mstsc %s" % "lala")