USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_Svr_Dr_Sync_L]    Script Date: 2022-02-11 ¿ÀÀü 9:30:19 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_Svr_Dr_Sync_L](
	[hostName] [varchar](30) NOT NULL,
	[CollectDT] [varchar](8) NOT NULL,
	[MESSAGE_TEXT] [varchar](2048) NOT NULL,
	[RGPR_ID] [varchar](30) NULL,
	[RGST_DTM] [datetime] NULL,
	[MDFPR_ID] [varchar](30) NULL,
	[MDF_DTM] [datetime] NULL,
	[NOTE] [varchar](100) NULL
) ON [PRIMARY]
GO


