USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_Svr_Rsrc_Chk_L]    Script Date: 2022-02-11 ¿ÀÀü 9:30:29 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_Svr_Rsrc_Chk_L](
	[CollectDT] [varchar](8) NOT NULL,
	[CollectHH] [varchar](2) NOT NULL,
	[hostName] [varchar](30) NOT NULL,
	[cpuUse] [decimal](5, 2) NOT NULL,
	[memUse] [decimal](5, 2) NOT NULL,
	[diskChk] [int] NOT NULL,
	[prcsCnt] [int] NOT NULL,
	[RGPR_ID] [varchar](30) NULL,
	[RGST_DTM] [datetime] NULL,
	[MDFPR_ID] [varchar](30) NULL,
	[MDF_DTM] [datetime] NULL,
	[NOTE] [varchar](100) NULL,
 CONSTRAINT [PK_Svr_Rsrc_Chk_L] PRIMARY KEY CLUSTERED 
(
	[CollectDT] ASC,
	[CollectHH] ASC,
	[hostName] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


