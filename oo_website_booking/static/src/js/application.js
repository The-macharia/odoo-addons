odoo.define('oo_website_booking.application', function(require) {
    $(document).ready(function() {
        var ajax = require('web.ajax');
        var rpc = require('web.rpc');

        const createRow = (val) => {
            return `
                <div class="col-md-3">
                    <div class="booking-item" style="background-image: url(data:image/jpeg;base64,${ val.image })">
                    <div class="booking-price">${ val.price }  ${ val.currency_symbol }/Night</div>
                        <button id="btn_book" class="btn btn-primary">Book Now</button>
                    </div>
                 </div>
            `
        }


        $("button[name='btn_submit']").on('click', function(e) {

            return rpc.query({
                    args: [
                        []
                    ],
                    model: 'hotel.room.type',
                    method: 'search_read',
                    fields: ['name', 'price', 'currency_symbol', 'image']
                })
                .then(function(data) {
                    $('.results-heading').show();
                    for (let val in data) {
                        $("div[name='results']").append(createRow(data[val]));
                    }
                    document.getElementById("results").scrollIntoView();
                });

        });
    })
})