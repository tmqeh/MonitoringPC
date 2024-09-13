USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_Rds_Err_Chk_L]    Script Date: 2022-02-11 ¿ÀÀü 9:35:03 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_Rds_Err_Chk_L](
	[ServerHost] [varchar](100) NOT NULL,
	[CollectDT] [varchar](8) NOT NULL,
	[CollectHH] [varchar](2) NOT NULL,
	[MESSAGE_TEXT] [varchar](4096) NULL,
	[CollectDTM] [datetime] NULL,
	[RGPR_ID] [varchar](30) NULL,
	[RGST_DTM] [datetime] NULL,
	[MDFPR_ID] [varchar](30) NULL,
	[MDF_DTM] [datetime] NULL,
	[NOTE] [varchar](100) NULL
) ON [PRIMARY]
GO


