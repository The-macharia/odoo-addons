odoo.define( 'oo_website_booking.application', function ( require ) {
    $( document ).ready( function () {
        var ajax = require( 'web.ajax' );
        var rpc = require( 'web.rpc' );

        const createRow = ( val ) => {
            return `<div class='col-12'>${ val.name }< p ></p ></div >`
        }


        $( "button[name='btn_submit']" ).on( 'click', function ( e ) {
            // e.preventDefault();

            return rpc.query( {
                args: [[]],
                model: 'res.partner',
                method: 'search_read',
                fields: ['name']
            } )
                .then( function ( data ) {
                    for ( let val in data ) {
                        $( "div[name='results']" ).append( createRow( data[val] ) );
                    }
                    document.getElementById( "results" ).scrollIntoView();
                } );

        } );
    } )
} )
