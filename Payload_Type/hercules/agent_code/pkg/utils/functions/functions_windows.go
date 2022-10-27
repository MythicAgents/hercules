//go:build windows
// +build windows

package functions

import (
	"os"
	"os/user"
	"runtime"
)

func isElevated() bool {
	currentUser, _ := user.Current()
	return currentUser.Uid == "0"
}
func getArchitecture() string {
	return runtime.GOARCH
}
func getProcessName() string {
	name, err := os.Executable()
	if err != nil {
		return ""
	} else {
		return name
	}
}
func getDomain() string {
	return ""
}
func getStringFromBytes(data [65]byte) string {
	stringData := make([]byte, 0, 0)
	for i := range data {
		if data[i] == 0 {
			return string(stringData[:])
		} else {
			stringData = append(stringData, data[i])
		}
	}
	return string(stringData[:])
}
func getOS() string {
	return "windows"
}
func getUser() string {
	currentUser, err := user.Current()
	if err != nil {
		return ""
	} else {
		return currentUser.Username
	}
}
func getPID() int {
	return os.Getpid()
}
func getHostname() string {
	hostname, err := os.Hostname()
	if err != nil {
		return ""
	} else {
		return hostname
	}
}
