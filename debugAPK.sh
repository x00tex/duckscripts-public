#!/bin/sh

#####################################################################################################
#                                                                                                   #
# Author :- @PofMagicfingers                                                                        #
# Source :- https://gist.github.com/PofMagicfingers/1876d10935dd88ef866767cef44c140f                #
# Modified By :- poorduck                                                                           #
# Date: 2023-05-28                                                                                  #
# Description :- Script for enabling "AndroidManifest.xml" based "debuggable" flag in signed apk.   #
#                                                                                                   #
# Solution for error while installing - "INSTALL_FAILED_VERIFICATION_FAILURE"                       #
# $ adb shell settings put global verifier_verify_adb_installs 0                                    #
# $ adb shell settings put global package_verifier_enable 0                                         #
#                                                                                                   #
#####################################################################################################

if [ $# -eq 0 ]; then
  echo "Usage: $0 <APK_FILE> [APKTOOL_JAR]"
  exit 0
fi

APK=$1
APKTOOL="apktool"
installed_version=$($APKTOOL --version 2>/dev/null | awk '{print $1}')

# For "ERROR: brut.androlib.AndrolibException: brut.common.BrutException: could not exec (exit code = 1)",
# Try different versions of apktool jar from github.
if [ -n "$2" ] && [ -f "$2" ]; then
    echo "Using custom apktool jar: $2"
    APKTOOL="java -jar $2"
elif [ "$installed_version" != "" ]; then
    echo "Using installed version of apktool: $installed_version"
else
    echo "APKTOOL is not installed. Please install APKTOOL and try again."
    exit 1
fi

command -v keytool >/dev/null 2>&1 || { echo >&2 "I require keytool but it's not installed. Aborting."; exit 1; }
command -v jarsigner >/dev/null 2>&1 || { echo >&2 "I require jarsigner but it's not installed. Aborting."; exit 1; }

TMPDIR=`mktemp -d 2>/dev/null || mktemp -d -t 'apkdebug'`
DEBUG_APK="${APK%.*}.debug.apk"

if [ -f $APK ]; then
	(echo "=> Unpacking APK..." &&
	$APKTOOL -q d $APK -o $TMPDIR/app &&
	echo "=> Adding debug flag..." &&
	sed -i -e "s/android:debuggable=\"[^\"]*\" *//;s/<application /<application android:debuggable=\"true\" /" $TMPDIR/app/AndroidManifest.xml &&
	echo "=> Repacking APK..." &&
	$APKTOOL -q b $TMPDIR/app --use-aapt2  -o $DEBUG_APK &&
	echo "=> Signing APK..." &&
	keytool -genkey -noprompt \
	 -alias alias1 \
	 -dname "CN=Unknown, OU=Unknown, O=Unknown, L=Unknown, S=Unknown, C=Unknown" \
	 -keystore $TMPDIR/keystore \
	 -keyalg RSA \
	 -storepass password \
	 -keypass password &&
	jarsigner -keystore $TMPDIR/keystore -storepass password -keypass password $DEBUG_APK alias1 > /dev/null 2>&1 &&
	echo "=> Checking your debug APK..." &&
	(jarsigner -verify $DEBUG_APK > /dev/null 2>&1 &&
	echo "\n======" &&
	echo "Success!"
	echo "======\n" &&
	echo "(deleting temporary directory...)\n" &&
	echo "Your debug APK : $DEBUG_APK" &&
	rm -rf $TMPDIR)) || (echo "=====" && echo "Something failed :'(" && echo "Leaving temporary dir $TMPDIR if you want to inspect what went wrong.")
else
	echo "File not found: $APK"
fi
