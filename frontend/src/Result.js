import React from 'react';
//const util = require('util');

function ResultEntry(props) {

    // variables
    // let imageUrl = props.data.og_image;
    
    // css styling
    const imageStyle = {
        maxWidth: '200px',
	maxHeight: '200px',
	width: 'auto',
        height: 'auto'
    }    

    const spanDescriptionName = {
        fontWeight: 'bold',
    }

    const cacheDescriptionName = {
	fontSize: 'small',
    }

    const figureStyle = {
        float: 'left',
        marginRight: '15px',
        marginLeft: '10px',
        marginTop: '10px',
	width: '200px',
    }
	
    // create cached url
    var cacheurl = props.hostname + '/csc530/cacheddocs/' + props.data.stream_name;

    // return everything
    return(
        <div className="result">
          <div className="resultInfo">
	      {'og_image' in props.data && !(String(props.data.og_image).startsWith("/")) &&
		<figure style={figureStyle}>
		   <img src={props.data.og_image} alt={props.data.og_image} style={imageStyle} />
		</figure>
	      }
	      <div className="resultText">
              <span style={spanDescriptionName}><a href={props.data.id} target="_blank" rel="noopener noreferrer">{props.data.title}</a></span><br />
	      {props.data.id}<br />
	      Solr Score: {props.data.score}<br />
	      <span style={cacheDescriptionName}>[ <a href={cacheurl} target="_blank" rel="noopener noreferrer">Cached URL</a> ]</span>
	      </div>
          </div>
        </div>
    )
}

class Result extends React.Component {
  // eslint-disable-next-line
  constructor(props) {
    super(props);
  }

  render() {
    //console.log("Result-render(props)" + JSON.stringify(this.props));

    // bail out if this is too early
    if(typeof this.props.data === 'undefined' ||
       typeof this.props.data.size === 'undefined' ||
       this.props.data.size === null
    ) {
        return null;
    }

    // data from super
    const data = this.props.data;
    let realnum = Number(data.offset) + 1;
    let maxSize = Number(data.maxSize);
    let maxResult = Number(data.offset) + Number(data.size);
    if(maxResult > maxSize) { maxResult = maxSize; }

    //console.log("Result: " + data)
    //console.log("Size: " + data.size)
    //console.log("initial: " + this.props.initial);

    // if no results, then just return a "Not Found" message
    if(this.props.initial === 1) { return(<span>&nbsp;</span>); }

    else if(this.props.searchinprogress === 1) { return(<span>Searching...</span>); }

    else if(data.maxSize <= 0) {
        return (
            <h3>No results found. :-(</h3>
        );
    }

    // Map all the images in the data variable
    else {
        const myResults = data.response.docs.map((dat) => {
            return(<ResultEntry data={dat} key={dat.id} hostname={this.props.hostname}/>);
        })

        return (
            <div>
                <h3 style={{paddingLeft: '10px'}}>Displaying results {realnum} - {maxResult} of {maxSize} total results.</h3>
                {myResults}
            </div>
        );
    }
  }
}



// Export it
export default Result
