// credits: https://github.com/deepch/RTSPtoWebRTC

package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"
)

func main() {
	log.SetFlags(0)
	go serveHTTP()
	go serveStreams()
	sigs := make(chan os.Signal, 1)
	done := make(chan bool, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		sig := <-sigs
		log.Println(sig)
		done <- true
	}()
	<-done
}
