import React from 'react';
//const util = require('util');

function ResultEntry(props) {

    // variables
    let imageUrl = props.data.og_image;
    
    // css styling
    const imageStyle = {
        max_width: '200px',
	max_height: '200px',
	width: '200px',
        height: 'auto'
    }    

    const spanDescriptionName = {
        fontWeight: 'bold',
    }

    const figureStyle = {
        float: 'right',
        marginRight: '15px',
        marginLeft: '100px',
        marginTop: '10px',
    }

    // return everything
    return(
        <div className="result">
          <div className="resultInfo">
              <span style={spanDescriptionName}>Title: </span>{props.data.title}<br />
	      <span style={spanDescriptionName}>URL: </span><a href={props.data.id} target="_blank" rel="noopener noreferrer">{props.data.id}</a><br />
	      <span style={spanDescriptionName}>Score: </span>{props.data.score}<br />
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
            return(<ResultEntry data={dat} key={dat.id}/>);
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
