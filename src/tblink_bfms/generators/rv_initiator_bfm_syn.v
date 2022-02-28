/****************************************************************************
 * rv_initiator_bfm_sim.sv
 *
 ****************************************************************************/
`include "rv_macros.svh"

/**
 * Module: rv_initiator_bfm_syn
 * 
 * TODO: Add module documentation
 */
module rv_initiator_bfm_syn #(
		parameter ADDR = 1,
		parameter WIDTH = 32
		) (
		input				cclock,
		input				uclock,
		input				reset,
		input				hreq_i,
		output				hreq_o,
		`RV_TARGET_PORT(neti_, 8),
		`RV_INITIATOR_PORT(neto_, 8),
		output				i_valid,
		input				i_ready,
		output[WIDTH-1:0] 	i_dat
		);
	reg[WIDTH-1:0]		data_v;
	reg					data_v_put_i;
	reg					data_v_get_i;
	reg[1:0]			data_v_count = 0;
	
	reg					rsp_put_i;
	reg					rsp_get_i;
	
	wire ep_hreq_i, ep_hreq_o;
	
	reg hreq_o_r;
	
	always @(posedge uclock or posedge reset) begin
		if (reset) begin
			hreq_o_r <= 1'b0;
		end else begin
			hreq_o_r <= (
				hreq_i |
				(rsp_put_i != rsp_get_i) |
				ep_hreq_o
			);
		end
	end
	
	assign hreq_o = hreq_o_r;

	

	/*
	initial begin
		if (WIDTH > 64) begin
			$display("Error: rv_data_out_bfm %m -- WIDTH>64 (%0d)", WIDTH);
			$finish();
		end
		data_v[0] = {WIDTH{1'b0}};
		data_v[1] = {WIDTH{1'b0}};
	end
	 */
	
	reg						in_reset = 0;
	reg[1:0]				state;
	
	assign i_dat = data_v;
	assign i_valid = (state == 2'b01);
	
	always @(posedge cclock or posedge reset) begin
		if (reset) begin
			data_v_get_i <= 1'b0;
			data_v <= {WIDTH{1'b0}};
			rsp_put_i <= 1'b0;
			state <= {2{1'b0}};
		end else begin
			case (state)
				2'b00: begin // Wait for a request
					// Wrap in a function
					if (data_v_get_i != data_v_put_i) begin
						data_v_get_i <= ~data_v_get_i;
						state <= 2'b01;
					end
				end
				2'b01: begin // Wait for an ack
					if (i_valid && i_ready) begin
						_rsp();
						state <= 2'b10;
					end
				end
				2'b10: begin // TODO: wait for ack complete
					// Technically this isn't necessary due 
					// to controlled clock gating
					state <= 2'b00;
				end
			endcase
		end
	end    

	// Need to specify reset variables and values
	// Maybe use a macro?
	
    task _req(input reg[63:0] data);
    begin
		$display("rv-bfm: _req=%08h", data);
    	data_v <= data;
    	data_v_put_i <= ~data_v_put_i;
    end
    endtask
    
    task _rsp;
    	rsp_put_i <= ~rsp_put_i;
    endtask

	assign ep_hreq_i = 0;
	
	assign hreq_i = 0;
	
	`RV_WIRES(tipo_, 8);
	`RV_WIRES(tipi_, 8);
	
	tblink_rpc_ep #(
		.ADDR        (ADDR       )
		) u_ep (
		.uclock      (uclock     ), 
		.reset       (reset      ), 
		.hreq_i      (ep_hreq_i ), 
		.hreq_o      (ep_hreq_o ), 
		`RV_CONNECT(neti_, neti_),
		`RV_CONNECT(neto_, neto_),
		`RV_CONNECT(tipo_, tipo_),
		`RV_CONNECT(tipi_, tipi_)
		);
	
	reg[3:0] ep_state;
	reg[7:0] count;
	reg[7:0] rcount;
	reg[7:0] cmd;
	reg[7:0] id;
	reg[7:0] rdat[7:0];
	
	assign tipo_ready = (
			ep_state == 4'b0000 ||
			ep_state == 4'b0001 ||
			ep_state == 4'b0010 ||
			ep_state == 4'b0011
			);

	// TIPO state machine
	integer i;
	always @(posedge uclock or posedge reset) begin
		if (reset) begin
			ep_state <= {4{1'b0}};
			count <= {8{1'b0}};
			rcount <= {8{1'b0}};
			data_v_put_i <= 1'b0;
		end else begin
			case (ep_state)
				4'b0000: begin // Count
					if (tipo_valid && tipo_ready) begin
						count <= tipo_dat;
						rcount <= tipo_dat;
						ep_state <= 4'b0001;
					end
				end
				4'b0001: begin // Capture command
					if (tipo_valid && tipo_ready) begin
						cmd <= tipo_dat;
						rcount <= rcount - 1'b1;
						ep_state <= 4'b0010;
					end
				end
				4'b0010: begin // Capture id
					if (tipo_valid && tipo_ready) begin
						id <= tipo_dat;
						rcount <= rcount - 1'b1;
						ep_state <= 4'b0011;
					end
				end
				4'b0011: begin // Capture remainder of the data
					if (tipo_valid && tipo_ready) begin
						for (i=7; i>0; i=i-1) begin
							rdat[i] <= rdat[i-1];
						end
						rdat[0] <= tipo_dat;
						if (rcount == 0) begin
							// Process command
							ep_state <= 4'b0100;
						end
						rcount <= rcount - 1'b1;
					end
				end
				4'b0100: begin // Process command
					ep_state <= 4'b0000;
					$display("rv-bfm: cmd=%0d", cmd);
					case (cmd[0])
					1'b0: begin // Req
						$display("rv-bfm: Calling _req");
						_req({rdat[0], rdat[1], rdat[2], rdat[3], 
								rdat[4], rdat[5], rdat[6], rdat[7]});
					end
					default:
						ep_state <= 4'b0000;
					endcase
				end
			endcase
		end
	end
	
	// TIPI state machine
	reg[3:0]		tipi_state;
	reg[7:0]		tipi_dat_o;
	
	assign tipi_valid = |tipi_state;
	assign tipi_dat = tipi_dat_o;
	
	always @(posedge uclock or posedge reset) begin
		if (reset) begin
			tipi_state <= {4{1'b0}};
			tipi_dat_o <= {8{1'b0}};
			rsp_get_i <= 1'b0;
		end else begin
			case (tipi_state)
				4'b0000: begin
					if (rsp_get_i != rsp_put_i) begin
						tipi_state <= 4'b0001;
						tipi_dat_o <= {8{1'b0}};
					end
				end
				4'b0001: begin // DST
					if (tipi_valid && tipi_ready) begin
						tipi_dat_o <= 8'd1; // SZ
						tipi_state <= 4'b0010;
					end
				end
				4'b0010: begin // SZ
					if (tipi_valid && tipi_ready) begin
						tipi_dat_o <= 8'd1; // RSP
						tipi_state <= 4'b0011; 
					end
				end
				4'b0011: begin // RSP
					if (tipi_valid && tipi_ready) begin
						tipi_dat_o <= id; // ID
						tipi_state <= 4'b0100; 
					end
				end
				4'b0100: begin // ID
					if (tipi_valid && tipi_ready) begin
						rsp_get_i <= ~rsp_get_i;
						tipi_state <= 4'b0000; 
					end
				end
			endcase
		end
	end

endmodule

