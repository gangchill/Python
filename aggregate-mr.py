#!/usr/bin/python2.7
import pymongo as mo
client = mo.MongoClient()
db = client.warehouse
db.aggregatemr.drop()

mapper='''function(){
	emit(this.category, {
		numOfArticles : 1,
		sumOfQuantities : this.quantity,
		articlesList : [{
			_id : this._id,
			quantitiy : this.quantity
			}]			
		});
	}'''

reducer='''function(key,values){
	var result = {numOfArticles : 0, sumOfQuantities : 0, articlesList : []};
	for(i=0;i<values.length;i++){
        var value=values[i];
		result.numOfArticles += value.numOfArticles;
		result.sumOfQuantities += value.sumOfQuantities;
		result.articlesList=result.articlesList.concat(value.articlesList);
    }
	return result;
}'''

db.products.map_reduce(mapper,reducer, 'aggregatemr')
