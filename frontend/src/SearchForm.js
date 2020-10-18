import React from 'react';

class Navigation extends React.Component {
  constructor(props) {
    super(props);

    this.handleNavPrevious = this.handleNavPrevious.bind(this);
    this.handleNavNext = this.handleNavNext.bind(this);
  }

  handleNavPrevious(event) {
    this.props.handleSearchNavPrev(event);
  }

  handleNavNext(event) {
    this.props.handleSearchNavNext(event);
  }

  render() {

    let offset = Number(this.props.data.offset);
    let size = Number(this.props.data.size);
    let maxSize = Number(this.props.data.maxSize);
    
    let navPrev;
    if(offset <= 0) {
      navPrev = '< < <';
    } else {
      // eslint-disable-next-line
      navPrev = <a href='#' onClick={this.handleNavPrevious}>&lt; &lt; &lt;</a>;
    }

    let navNext;
    if(offset + size >= maxSize) {
      navNext = '> > >';
    } else {
      // eslint-disable-next-line
      navNext = <a href="#" onClick={this.handleNavNext}>&gt; &gt; &gt;</a>;
    }

    //console.log("nav o s m: " + offset + "-" + size + "-" + maxSize);

    return (
      <span>{navPrev} &nbsp; Navigation &nbsp; {navNext}</span>
    );
  };
}  

class SearchForm extends React.Component {
  constructor(props) {
    super(props);

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleSizeChange = this.handleSizeChange.bind(this);
    this.handleSearchNavPrev = this.handleSearchNavPrev.bind(this);
    this.handleSearchNavNext = this.handleSearchNavNext.bind(this);
  }

  // event handlers
  handleChange(event) {
    this.props.onSearchChange(event.target.value);
  }

  handleSizeChange(event) {
    this.props.onSizeChange(event.target.value);
  }

  handleSearchNavPrev(event) {
    this.props.onNavPrev(event.target.value);
  }

  handleSearchNavNext(event) {
    this.props.onNavNext(event.target.value);
  }

  handleSubmit(event) {
    event.preventDefault();
    this.props.onSearchSubmit();
  }

  render() {

    // searchvalue from super
    const searchvalue = this.props.searchvalue;
    const sizevalue = this.props.size;

    // the search bar return function
    return (
      <form onSubmit={this.handleSubmit}>
        <span className="searchSpan">Search: &nbsp;
          <input type="text" value={searchvalue} onChange={this.handleChange} /> &nbsp; 
          <input type="submit" value="Submit" />
          &nbsp; &nbsp;Results Shown: &nbsp;
          <select value={sizevalue} onChange={this.handleSizeChange}>
            <option value="5">5</option>
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
          &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;<Navigation data={this.props.data} handleSearchNavPrev={this.handleSearchNavPrev} handleSearchNavNext={this.handleSearchNavNext} />
        </span>
      </form>
    );
  }
}

// Export it
export default SearchForm
