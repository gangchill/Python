#!/usr/bin/awk -f


# update one pass variance
function varOnepass(var,prevsum,val,count){
	# return 0 if only one number has been processed so far
	if(count<2){
		return(0);
	}
	# update formula according script
	pcount=count-1;
	newVar = (pcount * var + (val - prevsum/pcount)* (val - (prevsum+val)/count))/count;
	return(newVar);
}

# combine two mean values
function combMean(mean1,mean2,count){
	return ((count*mean1+count*mean2)/(count+count));
}

# update the variance according script formula
function updateVar(var,mean,combmean){
	#0.5 is ok since both sides have the same length
	tmp = var+(mean+combmean)*(mean-combmean);
	return (0.5*tmp);
}

# recursive variance update according script
function recVar(var1,var2,mean1,mean2,mean12){
	return(updateVar(var1,mean1,mean12)+updateVar(var2,mean2,mean12));
}


# initialize variables
BEGIN{
	# naive sum / mean
	sum=0;
	count=0;
	
	# corrected values
	csum=0;
	c=0;

	# one pass variance
	var=0;
	
	# "recursive" variance
	stackfill[0]=0;
	meanstack[0,0]=0;
	meanstack[0,1]=0;
	maxlevel=0;
}
{
	#standard sum computation
	# remember previous sum
	prevsum=sum;
	sum+=$1;
	count++;

	# Kahan Summation
	y=$1-c;
	t=csum+y;
	c=(t-csum)-y;
	csum=t;

	# variance one pass
	var=varOnepass(var,prevsum,$1,count);		

	# "recursive mean / variance

	# increment the stacak fill on lvl 0
	meanstack[0,stackfill[0]]=$1;
	# increment stackfill value
	stackfill[0]++;
	level=0;
	# while the current level contains two
	# values we can combine them
	while(stackfill[level]==2){
		# set stackfill value to 0 if we
		# witness a new max level
		nlevel=level+1
		if(maxlevel<nlevel){
			stackfill[nlevel]=0;
		}
		# update the mean value
		meanstack[nlevel,stackfill[nlevel]]=combMean(meanstack[level,0],meanstack[level,1],2^level);
		# update the variance value
		varstack[nlevel,stackfill[nlevel]]=recVar(varstack[level,0],varstack[level,1],meanstack[level,0],meanstack[level,1],meanstack[nlevel,stackfill[nlevel]]);
		# reset the stackfill of the current level
		stackfill[level]=0;
		# increment stackfill for the new level
		stackfill[nlevel]++;
		# increment processed level
		level++;
	}
	# update the maxlevel
	if(maxlevel<level){
		maxlevel=level
	}
}


END{
	# not enough values
	if(count<1){
		print("no input values");
		exit(1)
	}
	# naive mean
	naivemean = sum/count;
	# kahan mean
	cmean=csum/count;
	# rec var and mean
	recvar=varstack[maxlevel,0];
	recmean=meanstack[maxlevel,0];

	# write output
	printf("sum=%.16e corrected sum=%.16e\ndifference: %.16e\n",sum,csum,sum-csum);
    	printf("mean=%.16e cor. mean=%.16e recursive mean=%.16e\n",naivemean,cmean,recmean);
    	printf("variance=%.16e rec. variance=%.16e\ndifference: %.16e\n",var,recvar,var-recvar);
    	print("\nstackfill/maxlevel: "stackfill[maxlevel]"/"maxlevel);
}
