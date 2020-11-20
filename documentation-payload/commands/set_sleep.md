+++
title = "set_sleep"
chapter = false
weight = 100
hidden = false
+++

## Summary

Modify the time between callbacks in seconds. 
- Needs Admin: False  
- Version: 1  
- Author: @its_a_feature_  

### Arguments

#### jitter

- Description: Percentage of C2's interval to use as jitter  
- Required Value: False  
- Default Value: None  

#### sleep

- Description: Number of seconds between checkins  
- Required Value: False  
- Default Value: None  

## Usage

```
set_sleep [interval] [jitter]
```

## MITRE ATT&CK Mapping

- T1029  
## Detailed Summary

