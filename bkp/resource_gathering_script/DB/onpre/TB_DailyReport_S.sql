USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_DailyReport_S]    Script Date: 2022-02-11 ¿ÀÀü 9:29:37 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_DailyReport_S](
	[CLCT_DTM] [datetime] NULL,
	[INST_ID] [int] NOT NULL,
	[JOB_NM] [varchar](100) NOT NULL,
	[IP_ADDR] [varchar](15) NULL,
	[CLU_NODE_NM] [varchar](100) NULL,
	[CLU_CMPS_YN] [varchar](1) NULL,
	[AGENT_WRK_FAIL_CNT] [int] NULL,
	[ERR_LOG_CNT] [int] NULL,
	[MEM_USE_PCT] [decimal](5, 2) NULL,
	[DRV1] [varchar](10) NULL,
	[USE1] [decimal](5, 2) NULL,
	[DRV2] [varchar](10) NULL,
	[USE2] [decimal](5, 2) NULL,
	[DRV3] [varchar](10) NULL,
	[USE3] [decimal](5, 2) NULL,
	[DRV4] [varchar](10) NULL,
	[USE4] [decimal](5, 2) NULL,
	[DRV5] [varchar](10) NULL,
	[USE5] [decimal](5, 2) NULL,
	[DRV6] [varchar](10) NULL,
	[USE6] [decimal](5, 2) NULL,
	[DRV7] [varchar](10) NULL,
	[USE7] [decimal](5, 2) NULL,
	[DRV8] [varchar](10) NULL,
	[USE8] [decimal](5, 2) NULL,
	[DRV9] [varchar](10) NULL,
	[USE9] [decimal](5, 2) NULL,
	[INP_DTM] [datetime] NOT NULL,
	[BLK_TM] [bigint] NULL
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[TB_DailyReport_S] ADD  DEFAULT (getdate()) FOR [INP_DTM]
GO


