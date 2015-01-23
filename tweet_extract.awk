#!/usr/bin/awk -f

BEGIN{ 
    FS = "\t"
    keyword = "[#@][a-zA-Z]+"
}

{
    hash=""
    at=""
    content=$3
    while(match(content,keyword)){
	m=substr(content,RSTART+1,RLENGTH-1)
	tag=substr(content,RSTART,1)
	if(tag=="#") {
	    hash= hash "," m
	}else{
	    at= at "," m
	}
	content=substr(content,RSTART+RLENGTH)
    }
    if(hash!="" || at!=""){
	printf("%s\t%s\t%s\t%s\n",$2,$15,substr(hash,2),substr(at,2))
    }

}
